from concurrent import futures
import contextlib
import datetime
import logging
import multiprocessing
import random
import socket
import sys
import time
import os
from typing import Any
import jwt
# import consts

import grpc
from grpc_reflection.v1alpha import reflection
from recommendation_service import video_recommendation_pb2
from recommendation_service import video_recommendation_pb2_grpc

from utils.upstash_utils import UpstashUtils
from simple_recommendation_v0 import SimpleRecommendationV0

_LOGGER = logging.getLogger(__name__)

_ONE_DAY = datetime.timedelta(days=1)
_PROCESS_COUNT = multiprocessing.cpu_count()
_THREAD_CONCURRENCY = 10 # heuristic
_BIND_ADDRESS = "[::]:50059"  # Fixed bind address


_AUTH_HEADER_KEY = "authorization"

# _PUBLIC_KEY = consts.RECSYS_JWT_PUB_KEY
# _JWT_PAYLOAD = {
#     "sub": "yral-recsys-server",
#     "company": "gobazzinga",
# }


# class SignatureValidationInterceptor(grpc.ServerInterceptor):
#     def __init__(self):
#         def abort(ignored_request, context):
#             context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid signature")

#         self._abort_handler = grpc.unary_unary_rpc_method_handler(abort)

#     def intercept_service(self, continuation, handler_call_details):
#         metadata_dict = dict(handler_call_details.invocation_metadata)
#         token = metadata_dict[_AUTH_HEADER_KEY].split()[1]
#         payload = jwt.decode(
#             token,
#             _PUBLIC_KEY,
#             algorithms=["EdDSA"],
#         )

#         if payload == _JWT_PAYLOAD:
#             return continuation(handler_call_details)
#         else:
#             print(f"Received payload: {payload}")
#             return self._abort_handler


class MLFeedServicer(video_recommendation_pb2_grpc.MLFeedServicer):
    def __init__(self):
        self.recommender = SimpleRecommendationV0()
        return

    # implement popular dags here as we`ll -- with filter posts
    def get_ml_feed(self, request, context):
        watch_history_uris = [item.video_id for item in request.watch_history] + [item.video_id for item in request.filter_posts]
        # successful_plays_uris = [item.video_id for item in request.success_history]
        successful_plays = [
        {
            'video_uri': item.video_id,
            'item_type': item.item_type,
            'percent_watched': item.percent_watched
        } for item in request.success_history
    ]
        num_results = request.num_results
        popular_videos = self.recommender.get_popular_videos(watch_history_uris, num_results) 
        recommendations = self.recommender.get_score_aware_recommendation(successful_plays, watch_history_uris, num_results)
        def create_feed_response(feed_items):
            return video_recommendation_pb2.MLFeedResponse(
                feed=[
                    video_recommendation_pb2.MLPostItemResponse(**item)
                    for item in feed_items
                ]
            )

        response_exploitation = [
            {'post_id': int(item['post_id']), 'canister_id': item['canister_id']}
            for item in recommendations
        ]
        response_exploration = [
            {'post_id': int(item['post_id']), 'canister_id': item['canister_id']}
            for item in popular_videos
        ]

        required_sample_size = self.recommender.sample_size
        current_sample_size = len(successful_plays)

        def calculate_exploit_score(len_sample, len_required): # to be replaced with RL based exploration exploitation
            if len_required == 0:
                return 0
            ratio = len_sample / len_required
            score = max(0, min(80, ratio * 80))
            return score

        exploit_score = calculate_exploit_score(current_sample_size, required_sample_size)
        
        exploitation_sample_size = int(exploit_score / 100 * num_results)
        exploration_sample_size = num_results - exploitation_sample_size

        print(f"Exploitation sample size: {exploitation_sample_size}")
        print(f"Exploration sample size: {exploration_sample_size}")

        if len(response_exploitation) < exploitation_sample_size:
            _LOGGER.warning(f"Could not obtain the desired exploitation sample size of {exploitation_sample_size}; returning all {len(response_exploitation)} items.")
            sampled_exploitation_feed = response_exploitation
        else:
            sampled_exploitation_feed = random.sample(response_exploitation, exploitation_sample_size)

        if len(response_exploration) < exploration_sample_size:
            _LOGGER.warning(f"Could not obtain the desired exploration sample size of {exploration_sample_size}; returning all {len(response_exploration)} items.")
            sampled_exploration_feed = response_exploration
        else:
            sampled_exploration_feed = random.sample(response_exploration, exploration_sample_size)

        combined_feed = sampled_exploitation_feed + sampled_exploration_feed
        random.shuffle(combined_feed)
        
        response = create_feed_response(combined_feed)



        return response


def _wait_forever(server):
    try:
        while True:
            time.sleep(_ONE_DAY.total_seconds())
    except KeyboardInterrupt:
        print("Killing the server")
        server.stop(None)
        import os # for testing env
        os.system("lsof -ti :50059 | xargs kill -9")

def _run_server():
    _LOGGER.info("Starting new server.")
    options = (("grpc.so_reuseport", 1),)

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=_THREAD_CONCURRENCY),
        # interceptors=(SignatureValidationInterceptor(),),
        options=options,
    )
    video_recommendation_pb2_grpc.add_MLFeedServicer_to_server(
        MLFeedServicer(), server
    )
    SERVICE_NAMES = (
        video_recommendation_pb2.DESCRIPTOR.services_by_name['MLFeed'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    server.add_insecure_port(_BIND_ADDRESS)
    server.start()
    _LOGGER.info(f"Server started on {_BIND_ADDRESS}")
    _wait_forever(server)

def main():
    multiprocessing.set_start_method("spawn", force=True)
    _LOGGER.info(f"Binding to '{_BIND_ADDRESS}'")
    sys.stdout.flush()
    
    
    workers = []
    for _ in range(_PROCESS_COUNT):
        worker = multiprocessing.Process(target=_run_server)
        worker.start()
        workers.append(worker)
    for worker in workers:
        worker.join()

if __name__ == "__main__":
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("[PID %(process)d] %(message)s")
    handler.setFormatter(formatter)
    _LOGGER.addHandler(handler)
    _LOGGER.setLevel(logging.INFO)
    main()