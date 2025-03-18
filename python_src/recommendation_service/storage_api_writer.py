# TODO: Move this to bigquery_utils
from google.cloud import bigquery_storage_v1
from google.cloud.bigquery_storage_v1 import types
from google.cloud.bigquery_storage_v1 import writer
from google.protobuf import descriptor_pb2
from google.oauth2 import service_account
import logging
import os
import json
import ml_feed_reports_pb2
import consts
from datetime import datetime
from utils.config import Config

# The list of columns from the table's schema to search in the given data to write to BigQuery.
TABLE_COLUMNS_TO_CHECK = [
    "reportee_user_id",
    "reportee_canister_id",
    "video_canister_id",
    "video_post_id",
    "video_uri",
    "parent_video_canister_id",
    "parent_video_post_id",
    "parent_video_uri",
    "reason",
    "report_timestamp",
    "report_type",
]


# Function to create a batch of row data to be serialized.
def create_row_data(data):
    row = ml_feed_reports_pb2.MLFeedReport()
    for field in TABLE_COLUMNS_TO_CHECK:
        if field in data:
            setattr(row, field, data[field])
    return row.SerializeToString()


class BigQueryStorageWriteAppend:

    def __init__(self, project_id, dataset_id, table_id, stream_name="_default"):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_id = table_id
        self.stream_name = stream_name
        # Initialize config for service credentials
        self.cfg = Config()

    def append_rows_proto2(self, data: dict):
        write_client = None
        append_rows_stream = None
        try:
            # Get service credentials from Config
            service_cred = self.cfg.get("service_cred")
            service_acc_creds = json.loads(service_cred)
            credentials = service_account.Credentials.from_service_account_info(
                service_acc_creds
            )

            # Create client with credentials
            write_client = bigquery_storage_v1.BigQueryWriteClient(
                credentials=credentials
            )
            parent = write_client.table_path(
                self.project_id, self.dataset_id, self.table_id
            )
            stream_name = f"{parent}/{self.stream_name}"
            print("stream_name", stream_name)

            # Log data for debugging
            for i, row in enumerate(data):
                logging.debug(f"Row {i} data: {row}")
                # Validate each required field is present and has correct type
                for field in TABLE_COLUMNS_TO_CHECK:
                    if field not in row:
                        logging.error(f"Missing required field {field} in row {i}")

            write_stream = types.WriteStream()

            # Create a template with fields needed for the first request.
            request_template = types.AppendRowsRequest()

            # The request must contain the stream name.
            request_template.write_stream = stream_name

            # Generating the protocol buffer representation of the message descriptor.
            proto_schema = types.ProtoSchema()
            proto_descriptor = descriptor_pb2.DescriptorProto()
            ml_feed_reports_pb2.MLFeedReport.DESCRIPTOR.CopyToProto(proto_descriptor)
            proto_schema.proto_descriptor = proto_descriptor
            proto_data = types.AppendRowsRequest.ProtoData()
            proto_data.writer_schema = proto_schema
            request_template.proto_rows = proto_data

            # Construct an AppendRowsStream to send an arbitrary number of requests to a stream.
            append_rows_stream = writer.AppendRowsStream(write_client, request_template)

            # Append proto2 serialized bytes to the serialized_rows repeated field using create_row_data.
            proto_rows = types.ProtoRows()
            for row in data:
                try:
                    serialized_row = create_row_data(row)
                    proto_rows.serialized_rows.append(serialized_row)
                except Exception as e:
                    logging.error(f"Error serializing row {row}: {e}")
                    raise

            # Appends data to the given stream.
            request = types.AppendRowsRequest()
            proto_data = types.AppendRowsRequest.ProtoData()
            proto_data.rows = proto_rows
            request.proto_rows = proto_data

            # Send the request and get the response
            response_future = append_rows_stream.send(request)

            # Wait for the response to complete before closing the stream
            response = response_future.result()

            print(f"Rows to table: '{parent}' have been written.")
        finally:
            # Close the stream and client when done
            # if append_rows_stream:
            #     append_rows_stream.close()
            # Note: Don't close the client here as it might be reused
            pass

        return True


if __name__ == "__main__":

    ##### Uncomment the below block to provide additional logging capabilities ######
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()],
    )
    ##### Uncomment the above block to provide additional logging capabilities ######

    # Load data once outside the loop
    data = [
        {
            "reportee_user_id": "reportee_user_id",
            "reportee_canister_id": "reportee_canister_id",
            "video_canister_id": "video_canister_id",
            "video_post_id": "123",
            "video_uri": "video_uri",
            "parent_video_canister_id": "parent_video_canister_id",
            "parent_video_post_id": "parent_video_post_id",
            "parent_video_uri": "parent_video_uri",
            "report_timestamp": str(datetime.now()),
            "report_type": "report_type",
            "reason": "reason",
        }
    ] * 3

    # Change this to your specific BigQuery project, dataset, table details
    project_id = consts.PROJECT_ID
    dataset_id = consts.DATASET
    table_id = consts.REPORT_VIDEO_TABLE.split(".")[-1].replace("`", "")

    bigquery_storage_writer = BigQueryStorageWriteAppend(
        project_id, dataset_id, table_id
    )
    bigquery_storage_writer.append_rows_proto2(data)
