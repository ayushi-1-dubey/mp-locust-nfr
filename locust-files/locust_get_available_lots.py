# -*- coding: utf-8 -*-

"""
This contains to load test of Url-Mapping of gRPC call with locust.
"""

from locust import User
from locust import TaskSet
import json
import grpc
# import gevent
import time

# Libs
from locust import task

from proto import inventory_manager_pb2
from proto import inventory_manager_pb2_grpc
from proto.MetadataClientInterceptor import MetadataClientInterceptor


class TesterClient:

    def __init__(self):
        self.host = "localhost:8092"
        self.interceptors = [MetadataClientInterceptor()]

    def get_available_lots(self, request: inventory_manager_pb2.GetAvailableLotsRequest) -> inventory_manager_pb2.LotResponse:

        stub = inventory_manager_pb2_grpc.InventoryManagerStub(grpc.intercept_channel(grpc.insecure_channel(
            self.host), *self.interceptors))
        resp = stub.GetAvailableLots(request=request)
        print(resp)


class PerfTaskSet(TaskSet):

    def on_start(self):
        pass

    def on_stop(self):
        pass

    def create_req_payload(self):
        with open("sample-load-data/get_available_lots.json", "r" ) as jsonfile:
            data = json.load(jsonfile)
            return data["request"]

    @task
    def get_available_lots(self):

        dict = self.create_req_payload()
        for req in range(0, len(dict)):
            payload_dict = dict[req]
            req_data = inventory_manager_pb2.GetAvailableLotsRequest(apob_id="1", product_id=payload_dict["product_id"])
            self.locust_request_handler("get_available_lots", req_data)

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
            "get_available_lots": self.client.get_available_lots
        }
        if grpc_name not in req_func_map:
            raise ValueError(f"gRPC name not supported [{grpc_name}]")
        return req_func_map[grpc_name]


class GetAvailableLotDetails(User):
    tasks = [PerfTaskSet]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.client = TesterClient()
