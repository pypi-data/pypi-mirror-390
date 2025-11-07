import os
import json
import pandas as pd
from pathlib import Path
import logging
from collections import defaultdict
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from prophecy_lineage_extractor.constants import *

GROUP_COL_LIST = [
            INBOUND_COL,
            CATALOG_COL,
            DB_COL,
            TABLE_COL,
            COLNAME_COL,
            COLTYPE_COL,
            COL_DESCRIPTION_COL,
            PIPELINE_NAME_COL,
            PROCESS_NAME_COL,
            PROCESS_DESCRIPTION
        ]


class BaseWriter(ABC):
    def __init__(self, project_id: str, pipeline_id_list: List[str], output_dir: str, recursive_extract: bool, run_for_all: bool, graph: Optional[Dict] = None):
        self.project_id = project_id
        self.output_dir = Path(output_dir)
        self.pipeline_id_list = pipeline_id_list
        # Create project-specific folder for JSON files
        self.project_folder = Path(output_dir) / self._sanitize_name(project_id)
        self.project_folder.mkdir(parents=True, exist_ok=True)
        self.temp_csv_path = Path(os.path.join(self.project_folder, 'temp_files'))
        self.run_for_all = run_for_all
        self.graph = graph  # Store dataset connections
        self.total_index = -1
        self.new_set_of_datasets = []
        self.datasets_processed = []
        self.datasets_to_process = []
        self.pipeline_dataset_map = {}
        self.datasets_schema = {}
        self.recursive_extract = recursive_extract

    def _sanitize_name(self, name: str) -> str:
        """
        Convert a name to a file-system safe string.

        Args:
            name: The name to sanitize

        Returns:
            File-system safe string
        """
        return name.replace(":", "_").replace("/", "_").replace("\\", "_").replace(" ", "_")

    def get_output_path(self, pipeline_nm_full_str = None):
        """Get final output path with correct format extension"""
        if pipeline_nm_full_str is None:
            return Path(os.path.join(self.output_dir, f"lineage_{self.project_id}.{self.fmt}"))
        else:
            return Path(os.path.join(self.output_dir, f"lineage_{self.project_id}_{pipeline_nm_full_str}.{self.fmt}"))

    def process_detailed_dataset_view(self, data: Dict) -> None:
        """
        Process detailed dataset view JSON and create CSV files.
        Overrides the BaseWriter implementation.

        Args:
            data: The detailed dataset view JSON
        """
        logging.info("Processing detailed dataset view")
        columns = data.get("columns", [])
        dataset_id = data.get("id", "NA")

        self.datasets_schema[dataset_id] = set()

        # Extract catalog, database, and table name
        catalog_name, database_name, table_name = self._get_dataset_info_from_id(dataset_id)

        for pipeline_id, datasets in self.pipeline_dataset_map.items():
            if dataset_id not in datasets:
                continue

            connection_type = datasets.get(dataset_id)
            pipeline_name = self._get_name(pipeline_id)
            lineage_data = []

            for column in columns:
                column_name = column.get("name")
                column_description = column.get("description", "")
                column_type = column.get("dataType", "String")
                self.datasets_schema[dataset_id].add(column_name.lower())

                # Process upstream transformations
                upstream_transformations = column.get("upstreamTransformations", [])
                # If no upstream transformations or non-recursive, add a simple entry
                if (not column.get("upstreamTransformations") or len(column.get("upstreamTransformations")) == 0 or
                    (connection_type == IS_INBOUND and not self.recursive_extract)):
                    lineage_data.append({
                        INBOUND_COL: connection_type,
                        CATALOG_COL: catalog_name if catalog_name else "default",
                        DB_COL: database_name if database_name else "default",
                        TABLE_COL: table_name,
                        COLNAME_COL: column_name,
                        COLTYPE_COL: column_type,
                        COL_DESCRIPTION_COL: column_description.replace("'", "") if column_description else "",
                        PIPELINE_NAME_COL: pipeline_name,
                        PROCESS_NAME_COL: 'SOURCE',
                        PROCESS_DESCRIPTION: f"Source Read from {column_name}",
                        UPSTREAM_TRANSFORMATION_COL: column_name
                    })
                    # continue

                else:

                    for upstream in upstream_transformations:
                        transform_pipeline_id = upstream.get("pipeline", {}).get("id", "Unknown")
                        transform_pipeline_name = upstream.get("pipeline", {}).get("name", "NA")

                        # Skip if transformation belongs to a different pipeline and
                        # we're not doing a recursive or run_for_all extraction
                        if (transform_pipeline_id != pipeline_id and
                            (connection_type == IS_INBOUND and not self.recursive_extract)):
                            continue

                        for transformation in upstream.get("transformations"):

                            process_name = transformation.get("processName", "Unknown")
                            process_description = transformation.get("comment", "NA")

                            # Add pipeline prefix for cross-pipeline transformations
                            if transform_pipeline_id != pipeline_id or self.run_for_all:
                                process_name = f"{process_name}"

                            # Format the transformation string
                            transformation_str = transformation.get("transformation")


                            lineage_data.append({
                                INBOUND_COL: connection_type,
                                CATALOG_COL: catalog_name if catalog_name else "default",
                                DB_COL: database_name if database_name else "default",
                                TABLE_COL: table_name,
                                COLNAME_COL: column_name,
                                COLTYPE_COL: column_type if column_type != '' else "Unknown",
                                COL_DESCRIPTION_COL: column_description.replace("'", "") if column_description else "",
                                PIPELINE_NAME_COL: transform_pipeline_name,
                                PROCESS_NAME_COL: process_name,
                                PROCESS_DESCRIPTION: process_description.replace("'", "") if process_description else "",
                                UPSTREAM_TRANSFORMATION_COL: transformation_str
                            })

            # Create DataFrame and save to CSV
            if lineage_data:
                df = pd.DataFrame(lineage_data)
                file_name = self.get_temp_file_nm(pipeline_name, dataset_id)
                self.append_to_csv(df, file_name, connection_type)
                self.datasets_processed.append(file_name)
                logging.info(f"Created lineage file for {pipeline_name}: {file_name}")

    def get_temp_file_nm(self, pipeline_name, dataset_id):
        return f"lineage_{self.project_id}_{pipeline_name}_{self._get_safe_dataset_id(dataset_id)}.csv"

    @property
    @abstractmethod
    def fmt(self) -> str:
        """File format extension (e.g., 'xlsx', 'csv')"""
        pass

    @property
    @abstractmethod
    def format(self) -> str:
        """Writer format ('excel', 'openLineage')"""
        pass

    def _process_pipeline(self, pipeline_id: str, datasets: List[str]) -> Optional[pd.DataFrame]:
        df = self.read_csvs(pipeline_id, datasets)
        if df is None:
            return None
        return self._process_dataframe(df)

    def _process_dataframe(self, df: pd.DataFrame):
        return df.groupby(GROUP_COL_LIST, as_index=False, dropna=False).agg({
            UPSTREAM_TRANSFORMATION_COL: lambda tr: ",\n".join([x if type(x)==str else str(x) for x in tr])
        })

    def read_csvs(self, pipeline_id: Optional[str] = None,
                  datasets: List[str] = []) -> Optional[pd.DataFrame]:
        """Read CSV files into DataFrame from temp directory"""
        dfs = []
        logging.info(f"DEBUG_WRITE: Reading CSVs from path = {self.temp_csv_path}")
        for csv_file in self.temp_csv_path.glob('*.csv'):
            if len(datasets) > 0:
                for dataset in datasets:
                    if self._should_process_file(csv_file, pipeline_id, dataset):
                        dfs.append(pd.read_csv(csv_file))
            else:
                if self._should_process_file(csv_file, pipeline_id, None):
                        dfs.append(pd.read_csv(csv_file))
        if dfs == []:
            return None
        return pd.concat(dfs).drop_duplicates() if len(dfs) > 0 else pd.DataFrame()

    def _should_process_file(self, csv_path: Path,
                             pipeline_id: Optional[str],
                             dataset= None) -> bool:

        base_condition = f"lineage_{self.project_id}_" in csv_path.name

        if not pipeline_id:
            return base_condition

        dataset_condition = False
        if dataset is None:
            dataset_condition = True
        else:
            dataset_condition = (
                    self.get_temp_file_nm(self._get_name(pipeline_id), dataset_id=dataset).split(".")[0] in csv_path.name
                )
        return (
            f"lineage_{self.project_id}_{self._get_name(pipeline_id)}" in csv_path.name
        ) and dataset_condition and base_condition

    def _get_name(self, id: str) -> str:
        """Extract safe name from ID"""
        return id.split("/")[-1]

    def append_to_csv(self, df: pd.DataFrame, file_name: str, connection_type: Optional[str] = None):
        """
        Append a DataFrame to an existing CSV file or create a new one if it doesn't exist.

        Args:
            df: The DataFrame to append.
            file_name: The name of the CSV file.
            connection_type: Optional connection type information.
        """
        # Ensure the temporary CSV directory exists
        self.temp_csv_path.mkdir(parents=True, exist_ok=True)
        file_path = self.temp_csv_path / file_name

        if df.empty:
            logging.info("CSV_WRITER: Received an empty DataFrame, nothing to write.")
            return

        # Add connection type if provided and column doesn't exist
        if connection_type and INBOUND_COL not in df.columns:
            df = df.copy()
            df[INBOUND_COL] = connection_type
        try:
            # Append data to a CSV file, creating it if it doesn't exist
            df.to_csv(file_path, mode='a', header=not file_path.exists(), index=False)
            logging.info(f"CSV_WRITER: Appended data to {file_path}")
        except Exception as e:
            logging.error(f"Failed to append data to {file_path}: {str(e)}")
            raise

    def _init_graph(self, graph):
        """
        Initialize graph data from the provided graph dictionary.

        Args:
            graph: Dictionary containing graph data with processes and connections
        """
        self.processes = graph.get("processes", {})
        self.connections = graph.get("connections", [])
        self.graph = graph

    def get_lineage_for_given_pipeline(self, graph, datasets):
        """
        Extract pipeline-dataset connections from summary view.

        Args:
            datasets: List of datasets

        Returns:
            List of datasets to process
        """
        if (self.run_for_all):
            self.pipeline_id_list = [
                process_str for process_str, process_json in
                    graph.get("processes", {}).items() if process_json.get("component") == "Pipeline"]
            self.recursive_extract = True


        connections = graph.get("connections")

        # Initialize with proper data structures
        pipeline_dataset_map = defaultdict(dict)
        dataset_connection_map = defaultdict(str)
        new_set_of_datasets = list()
        total_index = 0

        clean_pipeline_id_list = [val.replace(f"{self.project_id}/pipelines/", "") for val in self.pipeline_id_list]

        for connection in connections:
            src = connection.get("source").replace(f"{self.project_id}/pipelines/", "")
            target = connection.get("target").replace(f"{self.project_id}/pipelines/", "")

            # Pipeline -> Dataset (output)
            if src in clean_pipeline_id_list:
                if target in datasets:
                    pipeline_dataset_map[src].update({target: IS_OUTBOUND})
                    new_set_of_datasets.append(target)
                    dataset_connection_map[target] = IS_OUTBOUND
                    total_index += 1

            # Dataset -> Pipeline (input)
            if target in clean_pipeline_id_list:
                if src in datasets:
                    pipeline_dataset_map[target].update({src: IS_INBOUND})
                    new_set_of_datasets.append(src)
                    dataset_connection_map[src] = IS_INBOUND
                    total_index += 1

        # Update instance variables
        self.pipeline_dataset_map.update(dict(pipeline_dataset_map))
        self.new_set_of_datasets += list(set(new_set_of_datasets))

        if self.total_index == -1:
            self.total_index = total_index
        else:
            self.total_index += total_index
        return list(set(new_set_of_datasets))


    def get_dataset_from_summary_view(self, processes):
        """
        Extract datasets from summary view.

        Args:
            processes: JSON message with summary view data

        Returns:
            List of dataset IDs
        """
        logging.info("viewType is summaryView, getting datasets")
        # Extract all datasets from `processes`

        # Filter out all entries with component "Dataset" and collect their names
        datasets = [
            info["id"] for info in processes.values() if info.get("component") == "Dataset"
        ]
        logging.info(f"All datasets Total {len(datasets)}:\n {datasets}")
        return datasets


    def create_temp_files(self, data) -> None:
        """
        Create temporary files based on pipeline-dataset map.
        This method can be overridden by specific writers to create
        more detailed lineage information.

        Args:
            data: Data from readers
        """
        logging.info("Using default temp file creation method")
        # Default implementation - no additional processing
        self.process_detailed_dataset_view(data)


    def _get_dataset_info_from_id(self, dataset_id: str) -> tuple:
        """Extract catalog, database, and table name from dataset ID"""
        parts = dataset_id.split('/')
        if len(parts) == 1:
            parts = dataset_id.split('.')
            if len(parts) == 3:
                table_name = parts[-1]
                database_name = parts[-2] if len(parts) >= 2 else "default"
                catalog_name = parts[-3] if len(parts) >= 3 else "default"
                return catalog_name, database_name, table_name
        if len(parts) >= 3:
            table_name = parts[-1]
            # Try to extract database and catalog if available
            database_name = parts[-2] if len(parts) > 3 else "default"
            catalog_name = parts[-3] if len(parts) > 4 else "default"
            return catalog_name, database_name, table_name
        return "default", "default", dataset_id

    def _get_safe_dataset_id(self, dataset_id: str) -> str:
        """Create a safe filename from dataset ID"""
        return dataset_id.replace('/', '_').replace(':', '_').replace(".", "_")

    def _format_transformation(self, transformation: str) -> str:
        """Format a transformation string (can be overridden by subclasses)"""
        # Simple default implementation - remove extra whitespace
        return ' '.join(transformation.split())

    def delete_temp_files(self):
        path = self.temp_csv_path
        self.delete_file(path, recursive=True)

    def delete_file(self, path, recursive=False):
        """
        Delete a file or directory.
        """
        if not path.exists():
            logging.info(f"{path} does not exist. Nothing to delete.")
            return

        try:
            if path.is_file():
                path.unlink()
                logging.info(f"Deleted file {path}")
            elif path.is_dir():
                for child in path.iterdir():
                    if child.is_file():
                        child.unlink()
                    elif child.is_dir():
                        self.delete_file(child, recursive=True)
                path.rmdir()
                logging.info(f"Deleted directory {path}")
            else:
                logging.warning(f"{path} is not a valid file or directory.")
        except Exception as e:
            logging.error(f"Failed to delete {path}: {str(e)}")

    def write_to_format(self) -> Path:
        raise NotImplementedError("write_to_format not defined")

    def write(self) -> Path:
        logging.info(f"STARTED WRITING TO DATA FORMAT {self.format} has begun. Project Level File Name = {self.get_output_path()}")
        logging.info(f"PIPELINE_DATASET_MAP = {json.dumps(self.pipeline_dataset_map, indent=2)}")
        logging.info(f"CURRENT WORKING DIRECTORY = {os.getcwd()}; CURRENT_TEMP_FILE_DIR = {self.temp_csv_path}")
        logging.info(f"FILES IN CURRENT WORKING DIRECTORY = {os.listdir(os.getcwd())}")

        # Create temp files before processing

        # Check if temp directory exists and has files
        if self.temp_csv_path.exists():
            temp_files = list(self.temp_csv_path.glob('*.csv'))
            logging.info(f"FILES IN TEMP FILE DIRECTORY ({len(temp_files)}): {[f.name for f in temp_files]}")

        result = self.write_to_format()
        # self.delete_temp_files()
        logging.info(f"ENDED WRITING TO DATA FORMAT {self.format} has ended. Project Level File Name = {self.get_output_path()}")
        return result