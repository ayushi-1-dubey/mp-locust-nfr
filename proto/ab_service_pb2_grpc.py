# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import ab_service_pb2 as ab__service__pb2


class ABServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.IsEnabled = channel.unary_unary(
                '/com.flipkarthealthplus.marketplace.abService.ABService/IsEnabled',
                request_serializer=ab__service__pb2.ABServiceRequest.SerializeToString,
                response_deserializer=ab__service__pb2.ABServiceResponse.FromString,
                )


class ABServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def IsEnabled(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ABServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'IsEnabled': grpc.unary_unary_rpc_method_handler(
                    servicer.IsEnabled,
                    request_deserializer=ab__service__pb2.ABServiceRequest.FromString,
                    response_serializer=ab__service__pb2.ABServiceResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'com.flipkarthealthplus.marketplace.abService.ABService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ABService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def IsEnabled(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/com.flipkarthealthplus.marketplace.abService.ABService/IsEnabled',
            ab__service__pb2.ABServiceRequest.SerializeToString,
            ab__service__pb2.ABServiceResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)