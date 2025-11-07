import traceback
import json
import logging
from datetime import datetime

from prophecy_lineage_extractor.reader.base_reader import BasePipelineProcessor
from prophecy_lineage_extractor.reader.graphql import checkout_branch
from prophecy_lineage_extractor.reader.rest_req import hit_knowledge_graph_api
from prophecy_lineage_extractor.utils import (
    get_monitor_time, send_email
)
from prophecy_lineage_extractor.utils import (debug)


class RestPipelineProcessor(BasePipelineProcessor):


    def handle_summary_view_info(self, json_msg):
        """
        Handle didOpen message from WebSocket.

        Args:
            json_msg: JSON message
        """
        logging.info("Handling Summary Information")


        # Store the summary view for the writer to process
        processes = (
            json_msg.get("graph", {})
            .get("processes", {})
        )
        datasets = self.writer.get_dataset_from_summary_view(processes)
        debug(json_msg, f'rest_view_{self.project_id}')

        graph = json_msg.get("graph", {})
        self.writer._init_graph(graph)
        datasets = self.writer.get_lineage_for_given_pipeline(graph, datasets)
        self.writer.datasets_to_process = datasets



    def handle_dataset_details(self, dataset_json):
        """
        Handle didUpdate message from WebSocket.

        Args:
            dataset_json: JSON message
        """
        logging.info("Handling didUpdate")
        try:
            # Store the detailed dataset view for the writer to process
            dataset_id = dataset_json.get("id", "NA")
            # Mark this dataset as processed
            self.writer.create_temp_files(dataset_json)
            # Log the dataset being processed
            logging.info(f"Collected detailed view for dataset: {dataset_id}")
        except Exception as e:
            logging.error(f"Error: {str(e)}\nTraceback:\n{traceback.format_exc()}")

    def collect_temp_files_and_send_email(self):
        try:
            output_file = self.writer.write()
            logging.info(f"Final Report generated")
            if self.send_email:
                send_email(self.project_id, output_file, self.pipeline_id_list)
                logging.info(f"Final Report sent as mail for project_id = {self.project_id} ")
            else:
                logging.info(f"Final Report not sent as mail")

        except Exception as e:
            logging.error(f"Error during WebSocket processing: {e}\nTraceback:\n{traceback.format_exc()}")
            raise e


    def process(self):
        checkout_branch(self.project_id, self.branch)
        logging.info("Starting main Rest API thread..")
        # Make REST API Request. Add Retry etc.
        # On getting response, first run
        self.writer.delete_temp_files()
        response = hit_knowledge_graph_api(self.project_id, self.branch, self.pipeline_id_list)

        self.handle_summary_view_info(response)
        for dataset in response.get('datasets'):
            logging.info(
                    f"[START]: FETCH, Idle time"
                    f"""{datetime.now() - self.last_meaningful_message_time} seconds / {get_monitor_time()} seconds;\n
                         datasets_processed = {len(self.writer.datasets_processed)} OUT OF {self.writer.total_index}
                    """,
                )

            self.handle_dataset_details(dataset)

        self.collect_temp_files_and_send_email()

        logging.info(f"""[END]: Task Ended 
                    Accordingly we are closing websocket.
                    \nTemp Files Processed = {json.dumps(self.writer.datasets_processed, indent=2)}
                    \nDatasets Processed = {json.dumps(self.writer.datasets_to_process, indent=2)}""")




