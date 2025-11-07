import json
import os
import uuid
import numpy as np
import pandas as pd
import requests
from datetime import datetime
from typing import Dict, List, Tuple, Optional, IO
from pathlib import Path
import logging

from prophecy_lineage_extractor.utils import df_to_json_compliant_dict, convert_to_openlineage_column_transformation
from .base_writer import BaseWriter
from prophecy_lineage_extractor.constants import *


class OpenLineageWriter(BaseWriter):
    """
    Writer for OpenLineage format data that creates run events for Marquez.
    Generates and sends JSON files compatible with the OpenLineage specification.

    This class processes a graph-based lineage from connection_info JSON to generate
    OpenLineage events with detailed transformation information.
    """

    # Class constants
    SCHEMA_VERSION = "1-0-7"
    DEFAULT_NAMESPACE = "new"
    DEFAULT_API_TIMEOUT = 30  # Timeout for API calls in seconds

    @property
    def fmt(self) -> str:
        return "json"

    @property
    def format(self) -> str:
        return "openLineage"

    def __init__(self, project_id: str, pipeline_id_list: List[str], output_dir: str, recursive_extract: bool,  run_for_all: bool = False, send_events=True, api_timeout=None):
        """
        Initialize the OpenLineage writer.

        Args:
            project_id: Project identifier
            output_dir: Output directory for JSON files
            run_for_all: Whether to create project-level events
            send_events: Whether to send events to Marquez API
            api_timeout: Timeout for API calls in seconds (default: 30)
        """
        super().__init__(project_id, pipeline_id_list, output_dir, recursive_extract, run_for_all)


        # Core properties
        default_producer = "https://github.com/OpenLineage/OpenLineage/tree/main/integration/dbt" #os.environ.get(PROPHECY_URL, "prophecy-data-lineage")
        self.producer = os.environ.get("OPENLINEAGE_PRODUCER_URL", default_producer)
        self.schema_url = f"https://openlineage.io/spec/{self.SCHEMA_VERSION}/OpenLineage.json"
        self.send_events = send_events
        self.api_timeout = api_timeout or self.DEFAULT_API_TIMEOUT
        self.namespace = os.environ.get("OPENLINEAGE_NAMESPACE", "dbt")
        self.job_namespace = os.environ.get("OPENLINEAGE_JOB_NAMESPACE", "dbt")
        if self.producer == default_producer:
            logging.warning("Using default producer URL. Set environment variable OPENLINEAGE_PRODUCER_URL to customize.")
        if self.namespace == "dbt":
            logging.warning("Using default namespace 'dbt'. Set environment variables OPENLINEAGE_NAMESPACE to customize.")
        if self.job_namespace == "dbt":
            logging.warning("Using default namespace 'dbt'. Set environment variables OPENLINEAGE_JOB_NAMESPACE to customize.")

        # Initialize graph data structures
        self.dataset_details = {}
        self.processes = {}
        self.connections = []
        self.graph = {}

        # Initialize datasets schema
        self.datasets_schema = {}

        # Configure OpenLineage API endpoint
        self.openlineage_url = os.environ.get("OPENLINEAGE_URL", "localhost:3000//api/v1/lineage")
        if not self.openlineage_url.startswith(("http://", "https://")):
            self.openlineage_url = f"http://{self.openlineage_url}"
        self.api_endpoint = f"{self.openlineage_url}"

        # Store events for later reference
        self.events = []

        logging.info(f"OpenLineage API endpoint set to: {self.api_endpoint}")
        logging.info(f"JSON files will be stored in: {self.project_folder}")

    def write_to_format(self) -> Path:
        """
        Write OpenLineage events for each pipeline in the graph.

        Returns:
            Path to the index file containing references to all events
        """
        logging.info("Starting: Writing OpenLineage events")

        # Generate events
        all_event_paths = self._generate_events()

        # Create index file with all events
        index_path = self._create_index_file(all_event_paths)

        logging.info(f"Finished writing OpenLineage events, index file: {index_path}")
        return index_path

    def _generate_events(self) -> List[Path]:
        """
        Generate OpenLineage events for all pipelines in the graph.

        Returns:
            List of paths to all created event files
        """
        all_event_paths = []

        # Find all pipeline processes in the graph
        pipeline_processes = {
            process_id: process_data
            for process_id, process_data in self.processes.items()
            if process_data.get('component') == 'Pipeline'
        }

        logging.info(f"Generating events for {len(pipeline_processes)} pipelines from graph")

        # Create events for each pipeline
        for pipeline_id, pipeline_data in pipeline_processes.items():
            pipeline_name = pipeline_data.get('name', self._get_name(pipeline_id))
            logging.info(f"Creating events for pipeline: {pipeline_name}")

            # Generate events for this pipeline
            event_paths = self._create_pipeline_events(pipeline_id, pipeline_data)
            all_event_paths += event_paths

        # Send events to Marquez if enabled
        if self.send_events and all_event_paths:
            logging.info(f"Sending {len(all_event_paths)} events to OpenLineage API")
            self._send_events_to_api(all_event_paths)
        logging.info(f"Generated {len(all_event_paths)} OpenLineage events")
        return all_event_paths

    def _create_index_file(self, event_paths: List[Path]) -> Path:
        """
        Create an index file with references to all events.

        Args:
            event_paths: List of paths to event files

        Returns:
            Path to the index file
        """
        index_file = self.project_folder / f"index_{self.project_id}.json"

        index_data = {
            "project": self.project_id,
            "generated_at": datetime.now().isoformat(),
            "event_count": len(event_paths),
            "events": [
                {
                    "filename": path.name,
                    "path": str(path.relative_to(self.project_folder)),
                    "event_type": self._get_event_type_from_filename(path.name)
                }
                for path in event_paths
            ]
        }

        with open(index_file, "w") as f:
            json.dump(index_data, f, indent=2)

        logging.info(f"Created event index file: {index_file}")
        return index_file

    def _get_event_type_from_filename(self, filename: str) -> str:
        """
        Extract event type from filename.

        Args:
            filename: Name of the event file

        Returns:
            Event type (START, COMPLETE, or UNKNOWN)
        """
        if "start" in filename.lower():
            return "START"
        elif "complete" in filename.lower():
            return "COMPLETE"
        else:
            return "UNKNOWN"

    def _get_name(self, entity_id: str) -> str:
        """
        Extract name from entity ID.

        Args:
            entity_id: Entity identifier

        Returns:
            Name extracted from ID
        """
        if not entity_id:
            return "unknown"

        parts = entity_id.split('/')
        if len(parts) >= 3:
            return parts[2]  # Format: "project_id/type/name"

        return entity_id  # Return as-is if can't parse

    def _create_pipeline_events(self, pipeline_id: str, pipeline_data: Dict) -> List[Path]:
        """
        Create START and COMPLETE run events for a pipeline using graph data,
        including input/output relationships from connections.

        Args:
            pipeline_id: Pipeline identifier
            pipeline_data: Pipeline process data from graph

        Returns:
            List of paths to created event files
        """
        pipeline_name = pipeline_data.get('name', self._get_name(pipeline_id))

        # Extract input and output relationships from connections
        inputs, outputs = self._get_pipeline_inputs_outputs(pipeline_id)

        # Skip if no inputs or outputs
        if len(inputs)==0 and len(outputs)==0:
            logging.warning(f"Pipeline {pipeline_name} has no inputs or outputs, skipping")
            return []

        # Create events for the pipeline
        run_id = str(uuid.uuid4())
        description = f"Pipeline {pipeline_name} in project {self.project_id}"

        output_paths = []
        events_created = []

        # Create column-level lineage facet for job

        # Create events for START and COMPLETE
        for event_type in ["START", "COMPLETE"]:
            event = self._create_run_event(
                event_type=event_type,
                run_id=run_id,
                job_namespace=f"prophecy_{self.project_id}",
                job_name=pipeline_name,
                description=description,
                inputs=inputs,
                outputs=outputs
            )

            # Generate a unique filename
            file_name = f"{pipeline_name}_{event_type.lower()}.json"

            # Write to file
            output_path = self.project_folder / file_name
            with open(output_path, "w") as f:
                json.dump(event, f, indent=2)

            # Store event
            events_created.append({
                "path": output_path,
                "event": event
            })

            output_paths.append(output_path)

        # Store events for reference
        # self.events.extend(events_created)

        return output_paths

    def get_input_output_events(self, pipeline_id, datasets, is_input):
        events = {}
        dataset_field_dict = {}
        for dataset_id in datasets:
            df = self.read_csvs(pipeline_id, [dataset_id])
            if df is None:
                logging.error(f"NO CSV AVAILABLE FOR OPENLINEAGE pipeline_id={pipeline_id} dataset={dataset_id}")
                continue
            df = df.replace([float('inf'), float('-inf')], None)
            df[COLNAME_COL] = df[COLNAME_COL]
            group_columns = [
                INBOUND_COL,
                CATALOG_COL,
                DB_COL,
                TABLE_COL,
                COLNAME_COL,
                COLTYPE_COL,
                COL_DESCRIPTION_COL,
                PIPELINE_NAME_COL
            ]
            df = df[group_columns +[PROCESS_NAME_COL, PROCESS_DESCRIPTION, UPSTREAM_TRANSFORMATION_COL]]

            # Create transformation objects based on SQL expressions
            df['transformation'] = df.apply(convert_to_openlineage_column_transformation, axis=1)
            # Group by specified columns and convert to JSON objects
            df_agg = df.groupby(group_columns, group_keys=False, dropna=False).agg(transformations=('transformation', lambda x: list(x))).reset_index()
            df_agg = df_agg.rename(columns={COLNAME_COL: "name",COLTYPE_COL: "type",COL_DESCRIPTION_COL: "description"})
            df_agg["type"] = df_agg["type"].replace([None, 'NA', pd.NA, np.nan, "Unknown"], "String")
            df_agg["name"] = df_agg["name"].str.lower()
            df_agg = df_agg.replace([float('inf'), float('-inf'), np.nan], None)
            df_agg = df_agg.drop_duplicates(["name", "type"])
            df_agg_schema_with_transformation = df_agg[["name", "type", "description", "transformations"]]
            schema_with_transformation = df_to_json_compliant_dict(df_agg_schema_with_transformation, orient='records')
            # Store fields in dataset schema for lineage
            if dataset_id not in self.datasets_schema:
                field_names = [field.get("name").lower() for field in schema_with_transformation if field.get("name")]
                self.datasets_schema[dataset_id] = field_names
            dataset_field_dict[dataset_id] = schema_with_transformation
            # Determine directionality based on dataset type (input or output)
            # is_input = datasets[dataset_id] == IS_INBOUND

        for dataset_id, fields_schema_with_transformation in dataset_field_dict.items():
            dataset_event = self._create_dataset_object(pipeline_id, self._get_safe_dataset_id(dataset_id), fields_schema_with_transformation, is_input)
            events[dataset_event["name"]] = dataset_event

        return [v for k,v in events.items()]

    def _get_pipeline_inputs_outputs(self, pipeline_id: str) -> Tuple[List[Dict], List[Dict]]:
        """
        Get inputs and outputs for a pipeline using connections from the graph.

        Args:
            pipeline_id: Pipeline identifier

        Returns:
            Tuple of (inputs, outputs) lists containing dataset objects
        """
        clean_pipeline_id = pipeline_id.replace(f"{self.project_id}/pipelines/", "")
        datasets_linked = self.pipeline_dataset_map.get(clean_pipeline_id)
        input_datasets = {k:v for k,v in datasets_linked.items() if v == IS_INBOUND}
        output_datasets = {k:v for k,v in datasets_linked.items() if v == IS_OUTBOUND}
        inputs = self.get_input_output_events(pipeline_id, input_datasets, is_input = True)
        outputs = self.get_input_output_events(pipeline_id, output_datasets, is_input = False)
        return inputs, outputs

    def _add_column_lineage_facet(self, schema_fields: List[Dict]) -> (Dict, bool):
        column_lineage_facet = {
            "_producer": self.producer,
            "_schemaURL": f"https://openlineage.io/spec/{self.SCHEMA_VERSION}/ColumnLineageDatasetFacet.json",
            "fields": {}
        }

        has_column_lineage = False

        for field in schema_fields:
            field_name = field.get("name")
            transformations = field.get("transformations", [])

            if transformations:
                column_lineage_facet["fields"][field_name] = {
                    "transformations": transformations  # Use transformations as-is
                }
                has_column_lineage = True

        return column_lineage_facet, has_column_lineage

    def _create_dataset_object(self, pipeline_id: str, dataset_id: str, schema_fields: List[Dict], is_input: bool) -> Dict:
        """
        Create OpenLineage dataset object with schema information and column-level lineage.

        Args:
            pipeline_id: Pipeline identifier
            dataset_id: Dataset name
            schema_fields: List of fields with schema and transformation information
            is_input: Whether this is an input dataset

        Returns:
            OpenLineage dataset object
        """
        # Extract schema fields (without transformations)
        field_copy_dict = {}
        for field in schema_fields:
            # Create a copy without the transformations field
            field_copy_dict[field.get("name")] = {k: v for k, v in field.items() if k != 'transformations'}
        schema_only_fields = [v for k, v in field_copy_dict.items()]
        # Create dataset object with schema facet
        dataset_event = {
            "namespace": self.namespace,
            "name": dataset_id,
            "facets": {
                "schema": {
                    "_producer": self.producer,
                    "_schemaURL": f"https://openlineage.io/spec/{self.SCHEMA_VERSION}/SchemaDatasetFacet.json",
                    "fields": schema_only_fields
                },
                "dataSource": {
                    "_producer": self.producer,
                    "_schemaURL": f"https://openlineage.io/spec/{self.SCHEMA_VERSION}/DataSourceDatasetFacet.json",
                    "name": self.project_id,
                    "uri": f"{self.namespace}__{self.project_id}"
                }
            }
        }

        # Add column lineage facet if we have transformation information

        if not is_input:
            column_lineage_facet, has_column_lineage = self._add_column_lineage_facet(schema_fields)
            if has_column_lineage:
                dataset_event["facets"]["columnLineage"] = column_lineage_facet

        return dataset_event

    def _create_run_event(self, event_type: str, run_id: str, job_namespace: str,
                         job_name: str, description: str, inputs: List[Dict],
                         outputs: List[Dict], job_column_lineage: Optional[Dict] = None) -> Dict:
        """
        Create an OpenLineage run event.

        Args:
            event_type: Event type (START or COMPLETE)
            run_id: Unique run ID
            job_namespace: Job namespace
            job_name: Job name
            description: Job description
            inputs: List of input datasets
            outputs: List of output datasets
            job_column_lineage: Column lineage facet for the job

        Returns:
            OpenLineage run event
        """
        current_time = datetime.now().isoformat() + "Z"

        # Create base event
        event = {
            "eventType": event_type,
            "eventTime": current_time,
            "run": {
                "runId": run_id,
                "facets": {
                    "nominalTime": {
                        "_producer": self.producer,
                        "_schemaURL": f"https://openlineage.io/spec/{self.SCHEMA_VERSION}/NominalTimeRunFacet.json",
                        "nominalStartTime": current_time,
                        "nominalEndTime": current_time
                    }
                }
            },
            "job": {
                "namespace": self.job_namespace,
                "name": job_name,
                "facets": {
                    "documentation": {
                        "_producer": self.producer,
                        "_schemaURL": f"https://openlineage.io/spec/{self.SCHEMA_VERSION}/DocumentationJobFacet.json",
                        "description": description
                    }
                }
            },
            "producer": self.producer,
            "schemaURL": self.schema_url
        }

        # Add inputs and outputs
        if inputs:
            event["inputs"] = inputs

        if outputs:
            event["outputs"] = outputs

        # Add processing facet for COMPLETE events
        if event_type == "COMPLETE":
            event["run"]["facets"]["processing"] = {
                "_producer": self.producer,
                "_schemaURL": f"https://openlineage.io/spec/{self.SCHEMA_VERSION}/ProcessingEngineRunFacet.json",
                "version": "1.0.0",
                "name": "prophecy",
                "description": "Prophecy Data Lineage"
            }

        # Add column lineage facet to job if available
        # if job_column_lineage:
        #     event["job"]["facets"]["columnLineage"] = job_column_lineage

        return event

    def _get_safe_dataset_id(self, dataset_id: str) -> str:
        """
        Convert dataset ID to a safe format for OpenLineage.

        Args:
            dataset_id: Raw dataset identifier

        Returns:
            Safe dataset identifier for OpenLineage
        """
        return dataset_id.replace('/', '_').replace(':', '_')

    def _send_events_to_api(self, event_paths: List[Path]) -> None:
        """
        Send events to the OpenLineage API.

        Args:
            event_paths: List of paths to event files
        """
        success_count = 0
        failure_count = 0
        response_details = []

        for path in event_paths:
            try:
                # Read event file
                with open(path, "r") as f:
                    event = json.load(f)

                # Send POST request
                response = requests.post(
                    url=self.api_endpoint,
                    json=event,
                    headers={"Content-Type": "application/json"},
                    timeout=self.api_timeout
                )
                # Store response details
                response_detail = {
                    "path": str(path),
                    "status_code": response.status_code,
                    "event_type": event.get("eventType"),
                    "job_name": event.get("job", {}).get("name")
                }

                if response.status_code >= 400:
                    response_detail["error"] = response.text

                response_details.append(response_detail)

                # Check response
                if response.status_code >= 200 and response.status_code < 300:
                    logging.info(f"Successfully sent event {path.name}")
                    success_count += 1
                else:
                    logging.error(f"Failed to send event {path.name}: {response.status_code} - {response.text}")
                    failure_count += 1

            except requests.RequestException as e:
                logging.error(f"Network error sending event {path.name}: {str(e)}")
                failure_count += 1
                response_details.append({
                    "path": str(path),
                    "error": str(e),
                    "event_type": event.get("eventType", "UNKNOWN"),
                    "job_name": event.get("job", {}).get("name", "UNKNOWN") if "event" in locals() else "UNKNOWN"
                })
            except IOError as e:
                logging.error(f"File I/O error reading event {path.name}: {str(e)}")
                failure_count += 1
                response_details.append({
                    "path": str(path),
                    "error": f"File error: {str(e)}",
                    "event_type": "UNKNOWN",
                    "job_name": "UNKNOWN"
                })
            except ValueError as e:
                logging.error(f"JSON parsing error for event {path.name}: {str(e)}")
                failure_count += 1
                response_details.append({
                    "path": str(path),
                    "error": f"JSON parsing error: {str(e)}",
                    "event_type": "UNKNOWN",
                    "job_name": "UNKNOWN"
                })
            except Exception as e:
                logging.error(f"Unexpected error sending event {path.name}: {str(e)}")
                failure_count += 1
                response_details.append({
                    "path": str(path),
                    "error": f"Unexpected error: {str(e)}",
                    "event_type": "UNKNOWN",
                    "job_name": "UNKNOWN"
                })

        # Log summary
        logging.info(f"OpenLineage API summary: {success_count} events sent successfully, {failure_count} failed")

        # Save response details to a file
        response_file = os.path.join(self.project_folder, f"api_responses_{datetime.now().strftime('%Y%m%d%H%M%S')}.json")
        with open(response_file, "w") as f:
            json.dump({
                "summary": {
                    "success_count": success_count,
                    "failure_count": failure_count,
                    "total_count": len(event_paths),
                    "timestamp": datetime.now().isoformat()
                },
                "details": response_details
            }, f, indent=2)

        logging.info(f"API response details saved to {response_file}")

if __name__ == "__main__":
    writer = OpenLineageWriter(
                project_id="43339",
                output_dir="./test",
                run_for_all=True
            )
    writer.pipeline_dataset_map = {
      "43339/pipelines/local-lineage-pipeline-2": {
        "43339/datasets/customer_order_log_book": IS_INBOUND,
        "43339/datasets/recent_customer_order_log_book": IS_OUTBOUND,
        "43339/datasets/non_recent_customer_order_log_book": IS_OUTBOUND
      }
    }

    # Initialize any required schemas for testing
    writer.datasets_schema = {
        "43339/datasets/customer_order_log_book": ["customerid", "cardnumber", "amount", "datetime", "franchiseid", "paymentmethod", "product", "quantity", "totalprice", "transactionid", "unitprice"],
        "43339/datasets/recent_customer_order_log_book": ["customerid", "cardnumber", "amount", "datetime", "franchiseid", "paymentmethod", "product", "quantity", "totalprice", "transactionid", "unitprice"],
        "43339/datasets/non_recent_customer_order_log_book": ["customerid", "cardnumber", "amount", "datetime", "franchiseid", "paymentmethod", "product", "quantity", "totalprice", "transactionid", "unitprice"]
    }

    writer.write()