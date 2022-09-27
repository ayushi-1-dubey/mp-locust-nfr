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
import re

class TesterClient:

    def __init__(self):
        self.host = "localhost:8090"
        self.interceptors = [MetadataClientInterceptor()]
        self.list_of_fkh_lot_id = []


    def create_inv(self, request: distributor_service_pb2.CreateInventoryRequest) -> distributor_service_pb2.CreateInventoryResponse:
        stub = distributor_service_pb2_grpc.DistributorServiceStub(grpc.intercept_channel(grpc.insecure_channel(
            self.host), *self.interceptors))
        resp = stub.CreateInventory(request=request)
        return resp


class PerfTaskSet(TaskSet):

    def on_start(self):
        pass

    def on_stop(self):
        pass

    def create_req_payload(self):
        with open("sample-load-data/createInv_data.json", "r" ) as jsonfile:
            data = json.load(jsonfile)
            return data["request"]

    @task
    def create_inv(self):

        dict = self.create_req_payload()
        list_of_fkh_lot_id = []
        for req in range(0, len(dict)):
            payload_dict = dict[req]
            req_data = distributor_service_pb2.CreateInventoryRequest(distributor_apob_id="1", lot_attributes=self.lot_attributes(payload_dict), external_lot_id=self.external_lot_id(payload_dict))
            resp = self.locust_request_handler("create_inventory", req_data)
            fkh_lot_id_obj = {"fkh_lot_id": re.findall(r'"(.*?)"', str(resp))[0]}
            list_of_fkh_lot_id.append(fkh_lot_id_obj)
        with open("sample-load-data/fkh_lot_ids.json", "w") as outfile:
            obj = {"request": list_of_fkh_lot_id}
            outfile.write(json.dumps(obj, indent=4))

    def lot_attributes(self, payload_dict):

        mf_timestamp = Timestamp(seconds= payload_dict["lot_attributes"]["mfg_date"]["seconds"], nanos= payload_dict["lot_attributes"]["mfg_date"]["nanos"])
        exp_timestamp = Timestamp(seconds= payload_dict["lot_attributes"]["expiry_date"]["seconds"], nanos= payload_dict["lot_attributes"]["expiry_date"]["nanos"])
        return distributor_service_pb2.LotAttributes(product_id=payload_dict["lot_attributes"]["product_id"], batch_id=payload_dict["lot_attributes"]["batch_id"], expiry_date=exp_timestamp, mfg_date=mf_timestamp, quantity=payload_dict["lot_attributes"]["quantity"], sold_quantity=payload_dict["lot_attributes"]["sold_quantity"], mrp=payload_dict["lot_attributes"]["mrp"])

    def external_lot_id(self, payload_dict):
        return distributor_service_pb2.ExternalLotIdentifier(name="pk_lot", value=payload_dict["external_lot_id"]["value"])

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
            "create_inventory": self.client.create_inv
        }
        if grpc_name not in req_func_map:
            raise ValueError(f"gRPC name not supported [{grpc_name}]")
        return req_func_map[grpc_name]


class CreateInventory(User):
    tasks = [PerfTaskSet]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.client = TesterClient()
