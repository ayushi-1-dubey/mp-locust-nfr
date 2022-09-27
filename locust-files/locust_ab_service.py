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

from proto import ab_service_pb2
from proto import ab_service_pb2_grpc
from proto.MetadataClientInterceptor import MetadataClientInterceptor


class TesterClient:

    def __init__(self):
        self.host = "localhost:8096"
        self.interceptors = [MetadataClientInterceptor()]

    def ab_service(self, request: ab_service_pb2.ABServiceRequest) -> ab_service_pb2.ABServiceResponse:

        stub = ab_service_pb2_grpc.ABServiceStub(grpc.intercept_channel(grpc.insecure_channel(
            self.host), *self.interceptors))
        resp = stub.IsEnabled(request=request)

class PerfTaskSet(TaskSet):

    def on_start(self):
        pass

    def on_stop(self):
        pass

    def create_req_payload(self):
        with open("ab_service.json", "r" ) as jsonfile:
            data = json.load(jsonfile)
            return data["request"]

    @task
    def ab_service(self):

        dict = self.create_req_payload()
        for req in range(0, len(dict)):
            payload_dict = dict[req]
            req_data = ab_service_pb2.ABServiceRequest(userId=payload_dict["userId"], experimentName=payload_dict["experimentName"])
            self.locust_request_handler("ab_service", req_data)

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
            "ab_service": self.client.ab_service
        }
        if grpc_name not in req_func_map:
            raise ValueError(f"gRPC name not supported [{grpc_name}]")
        return req_func_map[grpc_name]


class ABService(User):
    tasks = [PerfTaskSet]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.client = TesterClient()
