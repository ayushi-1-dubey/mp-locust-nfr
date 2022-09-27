"""
This contains to load test of Url-Mapping of gRPC call with locust.
"""

from locust import User
from locust import TaskSet
import datetime
import grpc
import time
from google.protobuf.timestamp_pb2 import Timestamp
import json
import random
# Libs
from locust import task

from proto import distributor_service_pb2
from proto import distributor_service_pb2_grpc
from proto.MetadataClientInterceptor import MetadataClientInterceptor
from datetime import datetime, timedelta


class TesterClient:

    def __init__(self):
        self.host = "localhost:8090"
        self.interceptors = [MetadataClientInterceptor()]

    def update_sold_qty(self, request: distributor_service_pb2.UpdateInventorySoldQuantityUsingFKHLotIdRequest) -> distributor_service_pb2.UpdateInventorySoldQuantityUsingExternalLotIdResponse:

        stub = distributor_service_pb2_grpc.DistributorServiceStub(grpc.intercept_channel(grpc.insecure_channel(
            self.host), *self.interceptors))
        resp = stub.UpdateInventorySoldQuantityUsingFKHLotId(request=request)
        print(resp)


class PerfTaskSet(TaskSet):

    def on_start(self):
        pass

    def on_stop(self):
        pass

    def create_req_payload(self):
        with open("sample-load-data/fkh_lot_ids.json", "r" ) as jsonfile:
            data = json.load(jsonfile)
            return data["request"]

    @task
    def update_sold_qty(self):

        dict = self.create_req_payload()
        for req in range(0, len(dict)):
            payload_dict = dict[req]
            req_data = distributor_service_pb2.UpdateInventorySoldQuantityUsingFKHLotIdRequest(fkh_lot_id=payload_dict["fkh_lot_id"], distributor_apob_id="1", sold_quantity=50)
            self.locust_request_handler("update_sold_qty_using_fkhlot_id", req_data)

    def locust_request_handler(self, grpc_name, req_data):
        req_func = self._get_request_function(grpc_name)

        start = time.time()
        result = None
        try:
            print("req: " , req_data)
            result = req_func(req_data)
            print(result)
        except Exception as e:
            total = int((time.time() - start) * 1000)
            self.user.environment.events.request_failure.fire(
                request_type="grpc", name=grpc_name, response_time=total, response_length=0, exception=e)
        else:
            total = int((time.time() - start) * 1000)
            self.user.environment.events.request_success.fire(
                request_type="grpc", name=grpc_name, response_time=total, response_length=0)
        return result

    def _get_request_function(self, grpc_name):
        req_func_map = {
            "update_sold_qty_using_fkhlot_id": self.client.update_sold_qty
        }
        if grpc_name not in req_func_map:
            raise ValueError(f"gRPC name not supported [{grpc_name}]")
        return req_func_map[grpc_name]


class UpdateSoldQuantityUsingFKHLotId(User):
    tasks = [PerfTaskSet]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.client = TesterClient()
