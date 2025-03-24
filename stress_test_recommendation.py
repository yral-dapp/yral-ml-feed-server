import time
import statistics
from concurrent.futures import ThreadPoolExecutor
import logging
import sys
from python_src.recommendation_service.clean_recommendation_report_filtered_v0 import CleanRecommendationReportFilteredV0
import video_recommendation_pb2
import random

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='[PID %(process)d] [Thread %(thread)d] %(asctime)s - %(levelname)s - %(message)s',
                    stream=sys.stdout)
logger = logging.getLogger(__name__)

def run_recommendation_test(worker_id):
    """Run a single recommendation test and return the execution time"""
    try:
        start_time = time.time()
        
        # Use the same test data as in the original script
        outer_videos_watched = [
            "gs://yral-videos/53ec98e3b7314d4a86038cc064047b2d.mp4"
        ] * 10
        
        outer_successful_plays = outer_videos_watched[:10]
        outer_filter_responses = []
        outer_num_results = 25
        
        # Create test request objects
        watch_history = [
            video_recommendation_pb2.WatchHistoryItem(video_id=i)
            for i in outer_videos_watched
        ]

        success_history = [
            video_recommendation_pb2.SuccessHistoryItem(
                video_id=i, item_type="like_video", percent_watched=random.random()
            )
            for i in outer_successful_plays
        ]

        filter_posts = [
            video_recommendation_pb2.MLPostItem(
                post_id=post_id, canister_id=canister_id, video_id=video_id
            )
            for post_id, canister_id, video_id in outer_filter_responses
        ]

        # Create request
        request = video_recommendation_pb2.MLFeedRequest(
            canister_id=f"test_canister_random_{worker_id}",
            watch_history=watch_history,
            success_history=success_history,
            filter_posts=filter_posts,
            num_results=outer_num_results,
        )
        
        # Process request
        successful_plays_ = [
            {
                "video_uri": item.video_id,
                "item_type": item.item_type,
                "percent_watched": item.percent_watched,
            }
            for item in request.success_history
        ]
        outer_watch_history_uris = [item.video_id for item in request.watch_history] + [
            item.video_id for item in request.filter_posts
        ]
        num_results = request.num_results
        user_canister_id = request.canister_id
        
        # Create recommender instance and get recommendations
        recommender = CleanRecommendationReportFilteredV0()
        feed = recommender.get_collated_recommendation(
            successful_plays_, outer_watch_history_uris, num_results, user_canister_id
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        logger.info(f"Worker {worker_id} completed in {execution_time:.2f} seconds with {len(feed.feed)} recommendations")
        return execution_time
    except Exception as e:
        logger.error(f"Worker {worker_id} failed with error: {e}")
        return None

def run_stress_test(num_workers=100):
    """Run a stress test with the specified number of concurrent workers"""
    logger.info(f"Starting stress test with {num_workers} concurrent workers")
    
    execution_times = []
    successful_workers = 0
    failed_workers = 0
    
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        # Submit all workers
        future_to_worker = {executor.submit(run_recommendation_test, i): i for i in range(num_workers)}
        
        # Collect results as they complete
        for future in future_to_worker:
            worker_id = future_to_worker[future]
            try:
                execution_time = future.result()
                if execution_time is not None:
                    execution_times.append(execution_time)
                    successful_workers += 1
                else:
                    failed_workers += 1
            except Exception as e:
                logger.error(f"Worker {worker_id} raised an exception: {e}")
                failed_workers += 1
    
    # Calculate statistics
    if execution_times:
        avg_time = statistics.mean(execution_times)
        min_time = min(execution_times)
        max_time = max(execution_times)
        median_time = statistics.median(execution_times)
        p95_time = sorted(execution_times)[int(len(execution_times) * 0.95)]
        
        logger.info("Stress test results:")
        logger.info(f"Total workers: {num_workers}")
        logger.info(f"Successful workers: {successful_workers}")
        logger.info(f"Failed workers: {failed_workers}")
        logger.info(f"Average execution time: {avg_time:.2f} seconds")
        logger.info(f"Minimum execution time: {min_time:.2f} seconds")
        logger.info(f"Maximum execution time: {max_time:.2f} seconds")
        logger.info(f"Median execution time: {median_time:.2f} seconds")
        logger.info(f"95th percentile execution time: {p95_time:.2f} seconds")
    else:
        logger.error("All workers failed, no timing statistics available")

if __name__ == "__main__":
    run_stress_test(num_workers=100) 