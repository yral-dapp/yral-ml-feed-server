# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import video_recommendation_pb2 as video__recommendation__pb2

GRPC_GENERATED_VERSION = '1.68.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in video_recommendation_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class MLFeedStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.get_ml_feed = channel.unary_unary(
                '/ml_feed_py.MLFeed/get_ml_feed',
                request_serializer=video__recommendation__pb2.MLFeedRequest.SerializeToString,
                response_deserializer=video__recommendation__pb2.MLFeedResponse.FromString,
                _registered_method=True)
        self.get_ml_feed_clean = channel.unary_unary(
                '/ml_feed_py.MLFeed/get_ml_feed_clean',
                request_serializer=video__recommendation__pb2.MLFeedRequest.SerializeToString,
                response_deserializer=video__recommendation__pb2.MLFeedResponse.FromString,
                _registered_method=True)
        self.get_ml_feed_nsfw = channel.unary_unary(
                '/ml_feed_py.MLFeed/get_ml_feed_nsfw',
                request_serializer=video__recommendation__pb2.MLFeedRequest.SerializeToString,
                response_deserializer=video__recommendation__pb2.MLFeedResponse.FromString,
                _registered_method=True)
        self.get_ml_feed_clean_v1 = channel.unary_unary(
                '/ml_feed_py.MLFeed/get_ml_feed_clean_v1',
                request_serializer=video__recommendation__pb2.MLFeedRequest.SerializeToString,
                response_deserializer=video__recommendation__pb2.MLFeedResponse.FromString,
                _registered_method=True)
        self.get_ml_feed_nsfw_v1 = channel.unary_unary(
                '/ml_feed_py.MLFeed/get_ml_feed_nsfw_v1',
                request_serializer=video__recommendation__pb2.MLFeedRequest.SerializeToString,
                response_deserializer=video__recommendation__pb2.MLFeedResponse.FromString,
                _registered_method=True)
        self.report_video = channel.unary_unary(
                '/ml_feed_py.MLFeed/report_video',
                request_serializer=video__recommendation__pb2.VideoReportRequest.SerializeToString,
                response_deserializer=video__recommendation__pb2.VideoReportResponse.FromString,
                _registered_method=True)
        self.get_ml_feed_clean_v2 = channel.unary_unary(
                '/ml_feed_py.MLFeed/get_ml_feed_clean_v2',
                request_serializer=video__recommendation__pb2.MLFeedRequest.SerializeToString,
                response_deserializer=video__recommendation__pb2.MLFeedResponseV2.FromString,
                _registered_method=True)
        self.get_ml_feed_nsfw_v2 = channel.unary_unary(
                '/ml_feed_py.MLFeed/get_ml_feed_nsfw_v2',
                request_serializer=video__recommendation__pb2.MLFeedRequest.SerializeToString,
                response_deserializer=video__recommendation__pb2.MLFeedResponseV2.FromString,
                _registered_method=True)
        self.get_ml_feed_combined = channel.unary_unary(
                '/ml_feed_py.MLFeed/get_ml_feed_combined',
                request_serializer=video__recommendation__pb2.MLFeedRequest.SerializeToString,
                response_deserializer=video__recommendation__pb2.MLFeedResponseV2.FromString,
                _registered_method=True)
        self.get_ml_feed_clean_v2_deduped = channel.unary_unary(
                '/ml_feed_py.MLFeed/get_ml_feed_clean_v2_deduped',
                request_serializer=video__recommendation__pb2.MLFeedRequest.SerializeToString,
                response_deserializer=video__recommendation__pb2.MLFeedResponseV2.FromString,
                _registered_method=True)
        self.get_ml_feed_nsfw_v2_deduped = channel.unary_unary(
                '/ml_feed_py.MLFeed/get_ml_feed_nsfw_v2_deduped',
                request_serializer=video__recommendation__pb2.MLFeedRequest.SerializeToString,
                response_deserializer=video__recommendation__pb2.MLFeedResponseV2.FromString,
                _registered_method=True)
        self.get_ml_feed_combined_deduped = channel.unary_unary(
                '/ml_feed_py.MLFeed/get_ml_feed_combined_deduped',
                request_serializer=video__recommendation__pb2.MLFeedRequest.SerializeToString,
                response_deserializer=video__recommendation__pb2.MLFeedResponseV2.FromString,
                _registered_method=True)


class MLFeedServicer(object):
    """Missing associated documentation comment in .proto file."""

    def get_ml_feed(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def get_ml_feed_clean(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def get_ml_feed_nsfw(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def get_ml_feed_clean_v1(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def get_ml_feed_nsfw_v1(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def report_video(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def get_ml_feed_clean_v2(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def get_ml_feed_nsfw_v2(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def get_ml_feed_combined(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def get_ml_feed_clean_v2_deduped(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def get_ml_feed_nsfw_v2_deduped(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def get_ml_feed_combined_deduped(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_MLFeedServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'get_ml_feed': grpc.unary_unary_rpc_method_handler(
                    servicer.get_ml_feed,
                    request_deserializer=video__recommendation__pb2.MLFeedRequest.FromString,
                    response_serializer=video__recommendation__pb2.MLFeedResponse.SerializeToString,
            ),
            'get_ml_feed_clean': grpc.unary_unary_rpc_method_handler(
                    servicer.get_ml_feed_clean,
                    request_deserializer=video__recommendation__pb2.MLFeedRequest.FromString,
                    response_serializer=video__recommendation__pb2.MLFeedResponse.SerializeToString,
            ),
            'get_ml_feed_nsfw': grpc.unary_unary_rpc_method_handler(
                    servicer.get_ml_feed_nsfw,
                    request_deserializer=video__recommendation__pb2.MLFeedRequest.FromString,
                    response_serializer=video__recommendation__pb2.MLFeedResponse.SerializeToString,
            ),
            'get_ml_feed_clean_v1': grpc.unary_unary_rpc_method_handler(
                    servicer.get_ml_feed_clean_v1,
                    request_deserializer=video__recommendation__pb2.MLFeedRequest.FromString,
                    response_serializer=video__recommendation__pb2.MLFeedResponse.SerializeToString,
            ),
            'get_ml_feed_nsfw_v1': grpc.unary_unary_rpc_method_handler(
                    servicer.get_ml_feed_nsfw_v1,
                    request_deserializer=video__recommendation__pb2.MLFeedRequest.FromString,
                    response_serializer=video__recommendation__pb2.MLFeedResponse.SerializeToString,
            ),
            'report_video': grpc.unary_unary_rpc_method_handler(
                    servicer.report_video,
                    request_deserializer=video__recommendation__pb2.VideoReportRequest.FromString,
                    response_serializer=video__recommendation__pb2.VideoReportResponse.SerializeToString,
            ),
            'get_ml_feed_clean_v2': grpc.unary_unary_rpc_method_handler(
                    servicer.get_ml_feed_clean_v2,
                    request_deserializer=video__recommendation__pb2.MLFeedRequest.FromString,
                    response_serializer=video__recommendation__pb2.MLFeedResponseV2.SerializeToString,
            ),
            'get_ml_feed_nsfw_v2': grpc.unary_unary_rpc_method_handler(
                    servicer.get_ml_feed_nsfw_v2,
                    request_deserializer=video__recommendation__pb2.MLFeedRequest.FromString,
                    response_serializer=video__recommendation__pb2.MLFeedResponseV2.SerializeToString,
            ),
            'get_ml_feed_combined': grpc.unary_unary_rpc_method_handler(
                    servicer.get_ml_feed_combined,
                    request_deserializer=video__recommendation__pb2.MLFeedRequest.FromString,
                    response_serializer=video__recommendation__pb2.MLFeedResponseV2.SerializeToString,
            ),
            'get_ml_feed_clean_v2_deduped': grpc.unary_unary_rpc_method_handler(
                    servicer.get_ml_feed_clean_v2_deduped,
                    request_deserializer=video__recommendation__pb2.MLFeedRequest.FromString,
                    response_serializer=video__recommendation__pb2.MLFeedResponseV2.SerializeToString,
            ),
            'get_ml_feed_nsfw_v2_deduped': grpc.unary_unary_rpc_method_handler(
                    servicer.get_ml_feed_nsfw_v2_deduped,
                    request_deserializer=video__recommendation__pb2.MLFeedRequest.FromString,
                    response_serializer=video__recommendation__pb2.MLFeedResponseV2.SerializeToString,
            ),
            'get_ml_feed_combined_deduped': grpc.unary_unary_rpc_method_handler(
                    servicer.get_ml_feed_combined_deduped,
                    request_deserializer=video__recommendation__pb2.MLFeedRequest.FromString,
                    response_serializer=video__recommendation__pb2.MLFeedResponseV2.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'ml_feed_py.MLFeed', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('ml_feed_py.MLFeed', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class MLFeed(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def get_ml_feed(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/ml_feed_py.MLFeed/get_ml_feed',
            video__recommendation__pb2.MLFeedRequest.SerializeToString,
            video__recommendation__pb2.MLFeedResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def get_ml_feed_clean(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/ml_feed_py.MLFeed/get_ml_feed_clean',
            video__recommendation__pb2.MLFeedRequest.SerializeToString,
            video__recommendation__pb2.MLFeedResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def get_ml_feed_nsfw(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/ml_feed_py.MLFeed/get_ml_feed_nsfw',
            video__recommendation__pb2.MLFeedRequest.SerializeToString,
            video__recommendation__pb2.MLFeedResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def get_ml_feed_clean_v1(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/ml_feed_py.MLFeed/get_ml_feed_clean_v1',
            video__recommendation__pb2.MLFeedRequest.SerializeToString,
            video__recommendation__pb2.MLFeedResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def get_ml_feed_nsfw_v1(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/ml_feed_py.MLFeed/get_ml_feed_nsfw_v1',
            video__recommendation__pb2.MLFeedRequest.SerializeToString,
            video__recommendation__pb2.MLFeedResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def report_video(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/ml_feed_py.MLFeed/report_video',
            video__recommendation__pb2.VideoReportRequest.SerializeToString,
            video__recommendation__pb2.VideoReportResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def get_ml_feed_clean_v2(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/ml_feed_py.MLFeed/get_ml_feed_clean_v2',
            video__recommendation__pb2.MLFeedRequest.SerializeToString,
            video__recommendation__pb2.MLFeedResponseV2.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def get_ml_feed_nsfw_v2(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/ml_feed_py.MLFeed/get_ml_feed_nsfw_v2',
            video__recommendation__pb2.MLFeedRequest.SerializeToString,
            video__recommendation__pb2.MLFeedResponseV2.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def get_ml_feed_combined(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/ml_feed_py.MLFeed/get_ml_feed_combined',
            video__recommendation__pb2.MLFeedRequest.SerializeToString,
            video__recommendation__pb2.MLFeedResponseV2.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def get_ml_feed_clean_v2_deduped(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/ml_feed_py.MLFeed/get_ml_feed_clean_v2_deduped',
            video__recommendation__pb2.MLFeedRequest.SerializeToString,
            video__recommendation__pb2.MLFeedResponseV2.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def get_ml_feed_nsfw_v2_deduped(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/ml_feed_py.MLFeed/get_ml_feed_nsfw_v2_deduped',
            video__recommendation__pb2.MLFeedRequest.SerializeToString,
            video__recommendation__pb2.MLFeedResponseV2.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def get_ml_feed_combined_deduped(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/ml_feed_py.MLFeed/get_ml_feed_combined_deduped',
            video__recommendation__pb2.MLFeedRequest.SerializeToString,
            video__recommendation__pb2.MLFeedResponseV2.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
