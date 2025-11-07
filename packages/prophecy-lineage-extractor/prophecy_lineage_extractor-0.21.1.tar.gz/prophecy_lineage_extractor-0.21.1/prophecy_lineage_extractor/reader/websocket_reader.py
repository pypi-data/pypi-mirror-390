import traceback
import json
import logging
import threading
import time
from datetime import datetime, timedelta

import websocket

from prophecy_lineage_extractor import messages
from prophecy_lineage_extractor.constants import (
    PROPHECY_PAT, LONG_SLEEP_TIME, SLEEP_TIME,
)
from prophecy_lineage_extractor.reader.base_reader import BasePipelineProcessor
from prophecy_lineage_extractor.reader.graphql import checkout_branch
from prophecy_lineage_extractor.utils import (
    safe_env_variable, get_ws_url,
    get_monitor_time, send_email
)
from prophecy_lineage_extractor.utils import (
    debug
)


class WebsocketPipelineProcessor(BasePipelineProcessor):

    def update_monitoring_time(self):
        self.last_meaningful_message_time = datetime.now()
        logging.warning(
            f"[MONITORING]: Updating idle time, current idle time"
            f"= {datetime.now() - self.last_meaningful_message_time}"
        )

    def on_error(self, ws, error):
        logging.error(f"Error: {str(error)}\nTraceback:\n{traceback.format_exc()}")
        ws.close()
        exit(1)

    def handle_did_open(self, ws, json_msg):
        """
        Handle didOpen message from WebSocket.

        Args:
            ws: WebSocket connection
            json_msg: JSON message
        """
        logging.info("Handling didOpen")
        view_type = (
            json_msg.get("params", {})
            .get("lineage", {})
            .get("metaInfo", {})
            .get("viewType")
        )

        if view_type == "summaryView":
            # Store the summary view for the writer to process
            graph = json_msg.get("params", {}).get("lineage", {}).get("graph", {})
            processes = graph.get("processes", {})
            datasets = self.writer.get_dataset_from_summary_view(processes)
            debug(json_msg, f'summary_view_{self.project_id}')
            # import pdb; pdb.set_trace()
            datasets = self.writer.get_lineage_for_given_pipeline(graph, datasets)

            self.writer._init_graph(json_msg.get("params", {})\
                    .get("lineage", {})\
                    .get("graph", {})
                    )

            self.writer.datasets_to_process = datasets

            # Request detailed views for each dataset
            for dataset in datasets:
                logging.info(f"Requesting detailed view for dataset {dataset}")

                # Change active entity to the dataset
                ws.send(messages.change_active_entity(dataset))
                time.sleep(SLEEP_TIME)

                # Request detailed view
                ws.send(messages.detailed_view())
                time.sleep(LONG_SLEEP_TIME)

                # Return to summary view
                logging.info(f"Going back to summary view")
                ws.send(messages.summary_view())
                time.sleep(SLEEP_TIME)

    def handle_did_update(self, ws, json_msg):
        """
        Handle didUpdate message from WebSocket.

        Args:
            ws: WebSocket connection
            json_msg: JSON message
        """
        logging.info("Handling didUpdate")
        for change in json_msg.get("params", {}).get("changes", []):
            # Check if 'viewType' is present and equals 'detailedDatasetView'
            if (
                change.get("value", {}).get("metaInfo", {}).get("viewType")
                == "detailedDatasetView"
            ):
                try:
                    # Store the detailed dataset view for the writer to process
                    dataset_id = change.get("value", {}).get("dataset", {}).get("id", "NA")
                    debug(json_msg, f'detailed_view_{self.project_id}_{dataset_id.split("/")[-1]}')

                    # Mark this dataset as processed

                    self.writer.create_temp_files(change.get("value", {}).get("dataset", {}))

                    # Log the dataset being processed
                    logging.info(f"Collected detailed view for dataset: {dataset_id}")

                except Exception as e:
                    logging.error(f"Error: {str(e)}\nTraceback:\n{traceback.format_exc()}")
                    ws.close()


    def on_close(self, ws, close_status_code, close_msg):
        logging.info("### WebSocket closed ###")

    def on_message(self, ws, message):
        logging.info(f"\n\n### RECEIVED a message### ")
        try:
            json_msg = json.loads(message)
            if "method" in json_msg: # import json  json.dumps(json_msg, indent=2)
                method = json_msg["method"]
                logging.warning(f"method: {method}")
                # debug(json_msg, f'on_msg_{method.replace("/", "__")}')
                if method == "properties/didOpen":
                    self.update_monitoring_time()
                    self.handle_did_open(ws, json_msg)
                elif method == "properties/didUpdate":
                    self.update_monitoring_time()
                    self.handle_did_update(ws, json_msg)
                elif method in ["properties/publishDiagnostics", "window/logMessage", "ping"]:
                    pass
                elif method == "error":
                    logging.error(f"Error occurred:\n {json_msg['params']['msg']}")
                    raise Exception(f"Error occurred and we got method='Error'\n {json_msg}")
                else:
                    import pdb
                    pdb.set_trace()
                    raise Exception("method is not found in message", json_msg)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to decode JSON message: {e}")
            raise e

    def on_open(self, ws):
        self.writer.delete_temp_files()
        logging.info(f"\n\n### SENDING INIT PIPELINE for {self.project_id} ### ")
        # for pipeline_id in self.pipeline_id_list:
        ws.send(messages.init_pipeline(self.project_id, self.pipeline_id_list[0]))
        time.sleep(LONG_SLEEP_TIME)

    def end_ws(self):
        try:
            output_file = self.writer.write()
            logging.info(f"Excel report generated")
            if self.send_email:
                send_email(self.project_id, output_file, self.pipeline_id_list)
                logging.info(f"Excel report sent as mail for project_id = {self.project_id} ")
            else:
                logging.info(f"Excel report not sent as mail")

        except Exception as e:
            logging.error(f"Error during WebSocket processing: {e}\nTraceback:\n{traceback.format_exc()}")
            raise e
        finally:
            self.ws.close()

    def monitor_ws(self):
        logging.info("Monitor thread started.")
        time.sleep(SLEEP_TIME)
        monitor_time = get_monitor_time()
        logging.info(f"[MONITORING] Monitor Time: {monitor_time} seconds")
        while self.ws.keep_running:
            # global KEEP_RUNNING
            if (self.writer.total_index != -1 and
                    len(set(self.writer.datasets_processed)) >= (self.writer.total_index-1)):
                self.KEEP_RUNNING = False
            if datetime.now() - self.last_meaningful_message_time > timedelta(seconds=monitor_time):
                logging.warning(f"[MONITORING]: No meaningful messages received in the last {monitor_time} seconds, closing websocket")
                self.end_ws()
            elif not self.KEEP_RUNNING:
                logging.warning(f"""[MONITORING]: Task Ended. KEEP_RUNNING = {self.KEEP_RUNNING}; 
                            Accordingly we are closing websocket.
                            \nTemp Files Processed = {json.dumps(self.writer.datasets_processed, indent=2)}
                            \nDatasets Processed = {json.dumps(self.writer.datasets_to_process, indent=2)}""")
                self.end_ws()
            else:
                logging.warning(
                    f"[MONITORING]: KEEP_RUNNING={self.KEEP_RUNNING}, Idle time"
                    f"""{datetime.now() - self.last_meaningful_message_time} seconds / {get_monitor_time()} seconds;\n
                         datasets_processed = {len(self.writer.datasets_processed)} OUT OF {self.writer.total_index}
                    """,
                )
                if not self.KEEP_RUNNING:
                    logging.warning("COMPLETED REQUIRED TASK: Please end")
                    self.end_ws()
            time.sleep(SLEEP_TIME)
        logging.info("Monitor thread ended.")

    def run_websocket(self):
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(
            get_ws_url(),
            header={"X-Auth-Token": safe_env_variable(PROPHECY_PAT)},
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )

        monitor_thread = threading.Thread(target=self.monitor_ws, daemon=True)
        monitor_thread.start()

        self.ws.run_forever()

    def process(self):
        checkout_branch(self.project_id, self.branch)
        logging.info("Starting WebSocket thread..")
        ws_thread = threading.Thread(target=self.run_websocket, daemon=True)
        ws_thread.start()
        ws_thread.join()

