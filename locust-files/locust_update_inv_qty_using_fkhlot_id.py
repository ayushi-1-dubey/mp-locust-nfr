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

    def update_inv_using_fkhlot_id(self, request: distributor_service_pb2.UpdateInventoryQuantityUsingFKHLotIdRequest) -> distributor_service_pb2.UpdateInventoryQuantityUsingFKHLotIdResponse:

        stub = distributor_service_pb2_grpc.DistributorServiceStub(grpc.intercept_channel(grpc.insecure_channel(
            self.host), *self.interceptors))
        resp = stub.UpdateInventoryQuantityUsingFKHLotId(request=request)
        print(resp)


class PerfTaskSet(TaskSet):

    def on_start(self):
        pass

    def on_stop(self):
        pass

    def create_req_payload(self):
        with open("sample-load-data/update_inv_using_fkh_lot_id.json", "r" ) as jsonfile:
            data = json.load(jsonfile)
            return data["request"]

    def get_fkh_lot_id(self):
        with open("sample-load-data/fkh_lot_ids.json", "r" ) as jsonfile:
            fkh_lot_id = json.load(jsonfile)
            return fkh_lot_id["request"]

    @task
    def update_inv(self):

        dict = self.create_req_payload()
        fkh_lot_id = self.get_fkh_lot_id()
        for req in range(0, len(dict)):
            payload_dict = dict[req]
            fkh_lot_id_dict = fkh_lot_id[req]
            req_data = distributor_service_pb2.UpdateInventoryQuantityUsingFKHLotIdRequest(fkh_lot_id=fkh_lot_id_dict["fkh_lot_id"], distributor_apob_id="1", lot_attributes=self.lot_attributes(payload_dict), external_lot_id=self.external_lot_id(payload_dict))
            self.locust_request_handler("update_inventory_using_fkhlot_id", req_data)

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
            "update_inventory_using_fkhlot_id": self.client.update_inv_using_fkhlot_id
        }
        if grpc_name not in req_func_map:
            raise ValueError(f"gRPC name not supported [{grpc_name}]")
        return req_func_map[grpc_name]


class UpdateInventoryUsingFKHLotId(User):
    tasks = [PerfTaskSet]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.client = TesterClient()
