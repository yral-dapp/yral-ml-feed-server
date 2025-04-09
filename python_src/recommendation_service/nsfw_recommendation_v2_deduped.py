from config import Config

from concurrent.futures import ThreadPoolExecutor
from utils.bigquery_utils import BigQueryClient
from ast import literal_eval
import logging
import pandas as pd
import random
import grpc
import video_recommendation_pb2
import video_recommendation_pb2_grpc
import random
from recommendation_service.consts import (
    VIDEO_EMBEDDINGS_TABLE,
    GLOBAL_POPULAR_VIDEOS_TABLE,
    VIDEO_INDEX_TABLE,
    REPORT_VIDEO_TABLE,
    VIDEO_NSFW_TABLE,
    DUPLICATE_VIDEO_TABLE,
)

_LOGGER = logging.getLogger(__name__)

_LOGGER.setLevel(logging.INFO)


class NsfwRecommendationV2Deduped:
    def __init__(self):
        cfg = Config()
        self.bq = BigQueryClient()
        # self.upstash_db = UpstashUtils()
        ### hyper-parameters
        self.sample_size = 5  # number of successful plays to sample
        self.video_bucket_name = cfg.get("video_bucket_name")
        self.logging = cfg.get("logging")

    def fetch_embeddings(self, uri_list):
        """
        Fetches embeddings for the given list of URIs from BigQuery.

        Args:
            uri_list (list): A list of URIs for which to fetch embeddings.

        Returns:
            pandas.DataFrame: A DataFrame containing the embeddings.
        """
        query = f"""
        SELECT uri, post_id, canister_id, timestamp, embedding
        FROM {VIDEO_EMBEDDINGS_TABLE}
        WHERE uri IN UNNEST({uri_list})
        """
        return self.bq.query(query)

    def sample_successful_plays(self, successful_plays):
        """
        Samples a subset of successful plays based on their like status and watch duration.

        This function calculates a score for each video based on whether it was liked and the percentage
        of the video that was watched. It then performs weighted sampling to select a subset of videos.

        Args:
            successful_plays (list of dict): A list of dictionaries where each dictionary contains
                                             'video_uri', 'item_type' (either 'video_duration_watched' or 'like_video'),
                                             and 'percent_watched' (a float representing the percentage of the video watched).

        Returns:
            list of str: A list of video URIs that have been sampled based on their scores.
        """
        scores = {}
        for play in successful_plays:
            like_score = 1 if play["item_type"] == "like_video" else 0
            watch_duration_score = (
                play["percent_watched"] / 100
            )  # assuming the values are between 0 and 100 in the cannister
            score = (like_score + watch_duration_score) / 2
            scores[play["video_uri"]] = score

        sample_size = min(
            len(set([i["video_uri"] for i in successful_plays])), self.sample_size
        )
        uris = list(scores.keys())
        weights = list(scores.values())
        vdf_sample = random.choices(uris, weights=weights, k=sample_size)

        return vdf_sample

##
# Popularity
## 
    def get_popular_videos(
        self, watch_history_uris, num_results, user_canister_id
    ):  # TODO : add nsfw tag in the global popular videos l7d
        # Construct the SQL query
        video_ids = [
            uri.split("/")[-1].split(".")[0] for uri in watch_history_uris
        ]  # the script would break if the format is not .mp4
        watched_video_ids = ", ".join(
            f"'{video_id}'" for video_id in video_ids
        )  # will have to check till how much watch history is allowed in bigquery
        if watched_video_ids != "":
            # video_uri <> video_id is getting interchanged and converted since 
            # we have a mix of uri and video_id throughout. Changing the bucket 
            # name will impact this. This needs to be refactored.
            query = f"""
            SELECT video_id, global_popularity_score, nsfw_probability
            FROM {GLOBAL_POPULAR_VIDEOS_TABLE}
            WHERE video_id NOT IN ({watched_video_ids})
            AND (nsfw_ec = 'nudity' OR nsfw_ec = 'explicit')
            AND NOT EXISTS (
                SELECT 1 FROM {REPORT_VIDEO_TABLE}
                WHERE SUBSTR(video_uri, 18, ABS(LENGTH(video_uri) - 21)) = video_id
                AND reportee_canister_id = '{user_canister_id}'
            )
            AND NOT EXISTS (
                SELECT 1 FROM yral_ds.video_deleted
                WHERE video_id = {GLOBAL_POPULAR_VIDEOS_TABLE}.video_id
            )
            AND NOT EXISTS (
                SELECT 1 FROM {DUPLICATE_VIDEO_TABLE}
                WHERE video_id = {GLOBAL_POPULAR_VIDEOS_TABLE}.video_id
                AND exact_duplicate = True
            )
            AND nsfw_probability > 0.7
            ORDER BY global_popularity_score DESC
            LIMIT {int(4*num_results)}
            """
        else:
            query = f"""
            SELECT video_id, global_popularity_score, nsfw_probability
            FROM {GLOBAL_POPULAR_VIDEOS_TABLE}
            WHERE (nsfw_ec = 'nudity' OR nsfw_ec = 'explicit')
            AND NOT EXISTS (
                SELECT 1 FROM {REPORT_VIDEO_TABLE}
                WHERE SUBSTR(video_uri, 18, ABS(LENGTH(video_uri) - 21)) = video_id
                AND reportee_canister_id  = '{user_canister_id}'
            )
            AND NOT EXISTS (
                SELECT 1 FROM yral_ds.video_deleted
                WHERE video_id = {GLOBAL_POPULAR_VIDEOS_TABLE}.video_id
            )
            AND NOT EXISTS (
                SELECT 1 FROM {DUPLICATE_VIDEO_TABLE}
                WHERE video_id = {GLOBAL_POPULAR_VIDEOS_TABLE}.video_id
                AND exact_duplicate = True
            )
            AND nsfw_probability > 0.7
            ORDER BY global_popularity_score DESC
            LIMIT {int(4*num_results)}
            """
        rdf = self.bq.query(query)  # rdf - recent - popular videos data frame
        video_ids = rdf["video_id"].tolist()

        if not len(video_ids):
            return []

        video_ids_string = ", ".join(f'"{video_id}"' for video_id in video_ids)

        fetch_post_ids = f"""with uri_mapping as 
(
    SELECT distinct
    uri,
    SUBSTR(uri, 18, ABS(LENGTH(uri) - 21)) AS video_id,
    (SELECT value FROM UNNEST(metadata) WHERE name = 'post_id') AS post_id,
    (SELECT value FROM UNNEST(metadata) WHERE name = 'timestamp') AS timestamp,
    (SELECT value FROM UNNEST(metadata) WHERE name = 'canister_id') AS canister_id
    from {VIDEO_EMBEDDINGS_TABLE}
    WHERE NOT EXISTS (
        SELECT 1 FROM yral_ds.video_deleted
        WHERE gcs_video_id = uri
    )
)
select video_id, post_id, canister_id 
from uri_mapping 
where video_id in ({video_ids_string})"""

        mdf = self.bq.query(fetch_post_ids)  # mdf - metadata dataframe
        mdf = mdf[(mdf.post_id.isna() == False) & (mdf.canister_id.isna() == False)]
        
        # Join the results with nsfw_probability
        if not mdf.empty and not rdf.empty:
            mdf = pd.merge(mdf, rdf[['video_id', 'nsfw_probability']], on='video_id', how='left')
        
        return mdf["post_id canister_id video_id nsfw_probability".split()].to_dict("records")

##
# Exploitation
## 

    def get_score_aware_recommendation(
        self, sample_uris, watch_history_uris, num_results=10, user_canister_id=None
    ):
        """
        Generates a list of recommended post IDs based on the sample URIs and watch history.

        Args:
            sample_uris (list of str): A list of URIs representing the sample videos.
            watch_history_uris (list of str): A list of URIs representing the user's watch history.
            num_results (int, optional): The number of results to return. Defaults to 10.
            user_canister_id (str, optional): The canister ID of the user. Defaults to "test_canister".

        Returns:
            list of dict: A list of dictionaries, where each dictionary contains 'canister_id' and 'post_id'
                          keys corresponding to the recommended posts.
        """
        if len(sample_uris) == 0:
            return []

        watch_history_uris_string = ",".join([f"'{i}'" for i in watch_history_uris])
        sample_uris_string = ",".join([f"'{i}'" for i in sample_uris])
        search_breadth = 2 * ((int(num_results**0.5)) + 1)

        vs_query = f"""
        with search_result as (
        SELECT base.uri, base.post_id, base.canister_id, distance FROM
        VECTOR_SEARCH(
            (
            SELECT * FROM {VIDEO_INDEX_TABLE}
            WHERE uri NOT IN ({watch_history_uris_string}) -- maintain a recency filter with date here / bloom
            AND is_nsfw = True 
            AND post_id is not null 
            AND canister_id is not null 
            AND NOT EXISTS (
                SELECT 1 FROM {REPORT_VIDEO_TABLE}
                WHERE video_uri = uri
                AND reportee_canister_id = '{user_canister_id}'
            )
            AND NOT EXISTS (
                SELECT 1 FROM yral_ds.video_deleted
                WHERE gcs_video_id = uri
            )
            AND NOT EXISTS (
                SELECT 1 FROM {DUPLICATE_VIDEO_TABLE}
                WHERE video_id = SUBSTR(uri, 18, ABS(LENGTH(uri) - 21))
                AND exact_duplicate = True
            )
            ),
            'embedding',
            (
            SELECT embedding
            FROM {VIDEO_INDEX_TABLE}
            WHERE uri IN ({sample_uris_string})
            ),
            top_k => 1000
        )
        )
        SELECT search_result.uri, search_result.post_id, search_result.canister_id, search_result.distance, 
               video_nsfw_agg.probability as nsfw_probability,
               SUBSTR(search_result.uri, 18, ABS(LENGTH(search_result.uri) - 21)) AS video_id
        FROM search_result
        LEFT JOIN {VIDEO_NSFW_TABLE} as video_nsfw_agg
        ON search_result.uri = video_nsfw_agg.gcs_video_id
        where video_nsfw_agg.probability > 0.7
        ORDER BY distance 
        LIMIT {search_breadth}
        """
        try:
            result_df = self.bq.query(vs_query).drop_duplicates(subset=["uri"])
        except Exception as e:
            _LOGGER.warning(f"Error in nsfw vector search query: {e}")
            return []
        return result_df.to_dict("records")

##
# Recency based exploration
## 


    def get_random_recent_recommendation(
        self, sample_uris, watch_history_uris, num_results=10, user_canister_id=None
    ):
        """
        Gets random recent recommendations, filtered by reported videos for the specific user.

        Args:
            sample_uris (list of str): A list of URIs representing the sample videos.
            watch_history_uris (list of str): A list of URIs representing the user's watch history.
            num_results (int, optional): The number of results to return. Defaults to 10.
            user_canister_id (str, optional): The canister ID of the user. Defaults to "test_canister".

        Returns:
            list of dict: A list of dictionaries with recommended videos.
        """
        if not len(watch_history_uris):
            query = f"""
            with recent_uploads as (
            SELECT uri, post_id, canister_id, timestamp,
                   video_nsfw_agg.probability as nsfw_probability,
                   SUBSTR(uri, 18, ABS(LENGTH(uri) - 21)) AS video_id
            FROM {VIDEO_INDEX_TABLE} search_result
            LEFT JOIN {VIDEO_NSFW_TABLE} as video_nsfw_agg
            ON search_result.uri = video_nsfw_agg.gcs_video_id
            WHERE (search_result.nsfw_ec = 'nudity' OR search_result.nsfw_ec = 'explicit')
            AND video_nsfw_agg.probability > 0.7
            AND NOT EXISTS (
                SELECT 1 FROM {REPORT_VIDEO_TABLE}
                WHERE video_uri = uri
                AND reportee_canister_id = '{user_canister_id}'
            )
            AND NOT EXISTS (
                SELECT 1 FROM yral_ds.video_deleted
                WHERE gcs_video_id = uri
            )
            AND NOT EXISTS (
                SELECT 1 FROM {DUPLICATE_VIDEO_TABLE}
                WHERE video_id = SUBSTR(uri, 18, ABS(LENGTH(uri) - 21))
                AND exact_duplicate = True
            )
            order by TIMESTAMP_TRUNC(TIMESTAMP(SUBSTR(timestamp, 1, 26)), MICROSECOND) desc
            limit {4*num_results}
            )
            select * from recent_uploads
            order by RAND()
            limit {num_results}
            """

        else:
            watch_history_uris_string = ",".join([f"'{i}'" for i in watch_history_uris])
            query = f"""
            with recent_uploads as (
            SELECT uri, post_id, canister_id, timestamp,
                   video_nsfw_agg.probability as nsfw_probability,
                   SUBSTR(uri, 18, ABS(LENGTH(uri) - 21)) AS video_id
            FROM {VIDEO_INDEX_TABLE} search_result
            LEFT JOIN {VIDEO_NSFW_TABLE} as video_nsfw_agg
            ON search_result.uri = video_nsfw_agg.gcs_video_id
            WHERE uri NOT IN ({watch_history_uris_string})
            AND (search_result.nsfw_ec = 'nudity' OR search_result.nsfw_ec = 'explicit')
            AND video_nsfw_agg.probability > 0.7
            AND NOT EXISTS (
                SELECT 1 FROM {REPORT_VIDEO_TABLE}
                WHERE video_uri = uri
                AND reportee_canister_id = '{user_canister_id}'
            )
            AND NOT EXISTS (
                SELECT 1 FROM yral_ds.video_deleted
                WHERE gcs_video_id = uri
            )
            AND NOT EXISTS (
                SELECT 1 FROM {DUPLICATE_VIDEO_TABLE}
                WHERE video_id = SUBSTR(uri, 18, ABS(LENGTH(uri) - 21))
                AND exact_duplicate = True
            )
            order by TIMESTAMP_TRUNC(TIMESTAMP(SUBSTR(timestamp, 1, 26)), MICROSECOND) desc
            limit {4*num_results}
            )
            select * from recent_uploads
            order by RAND()
            limit {num_results}
            """

        result_df = self.bq.query(query).drop_duplicates(subset=["uri"])
        return result_df.to_dict("records")

##
# Recency based exploitation
## 

    def get_recency_aware_recommendation(
        self, sample_uris, watch_history_uris, num_results=10, user_canister_id=None
    ):
        """
        Generates a list of recommended post IDs based on the successful plays and watch history,
        applying weighted sampling based on video likes and watch duration. Maintains the search in the recently uploaded videos.

        Args:
            sample_uris (list of str): A list of URIs representing the sample videos.
                                             and 'percent_watched' (a float representing the percentage of the video watched).
            watch_history_uris (list of str): A list of URIs representing the user's watch history.
            num_results (int, optional): The number of results to return. Defaults to 10.
            user_canister_id (str, optional): The canister ID of the user. Defaults to "test_canister".

        Returns:
            list of dict: A list of dictionaries, where each dictionary contains 'canister_id' and 'post_id'
                          keys corresponding to the recommended posts.
        """
        if not len(sample_uris):
            return []
        search_breadth = 2 * ((int(num_results**0.5)) + 1)
        watch_history_uris_string = ",".join([f"'{i}'" for i in watch_history_uris])
        sample_uris_string = ",".join([f"'{i}'" for i in sample_uris])
        # Not filtering sample URI for nsfw, but only filtering the result  -- moving forward, we should see less and less nsfw in sample URI and it should eventually diminish.
        vs_query = f"""
        with search_result as (
        SELECT base.uri, base.post_id, base.canister_id, base.timestamp, distance FROM
        VECTOR_SEARCH(
            (
            SELECT * FROM {VIDEO_INDEX_TABLE} 
            WHERE uri NOT IN ({watch_history_uris_string})
            AND (nsfw_ec = 'nudity' OR nsfw_ec = 'explicit')
            AND post_id is not null 
            AND canister_id is not null 
            AND TIMESTAMP_TRUNC(TIMESTAMP(SUBSTR(timestamp, 1, 26)), MICROSECOND) > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 2 DAY)
            AND NOT EXISTS (
                SELECT 1 FROM {REPORT_VIDEO_TABLE}
                WHERE video_uri = uri
                AND reportee_canister_id = '{user_canister_id}'
            )
            AND NOT EXISTS (
                SELECT 1 FROM yral_ds.video_deleted
                WHERE gcs_video_id = uri
            )
            AND NOT EXISTS (
                SELECT 1 FROM {DUPLICATE_VIDEO_TABLE}
                WHERE video_id = SUBSTR(uri, 18, ABS(LENGTH(uri) - 21))
                AND exact_duplicate = True
            )
            ),
            'embedding',
            (
            SELECT embedding
            FROM {VIDEO_INDEX_TABLE}
            WHERE uri IN ({sample_uris_string})
            AND (nsfw_ec = 'nudity' OR nsfw_ec = 'explicit')
            AND post_id is not null
            AND canister_id is not null
            ),
            top_k => 1000,
            options => '{{"fraction_lists_to_search":0.6}}' -- CAUTION: This is high at the moment owing to the sparsity of the data, as an when we will have good number of recent uploads, this has to go down!
            )
        )
        select search_result.uri, search_result.post_id, search_result.canister_id, search_result.distance,
               video_nsfw_agg.probability as nsfw_probability,
               SUBSTR(search_result.uri, 18, ABS(LENGTH(search_result.uri) - 21)) AS video_id
        from search_result
        LEFT JOIN {VIDEO_NSFW_TABLE} as video_nsfw_agg
        ON search_result.uri = video_nsfw_agg.gcs_video_id
        where video_nsfw_agg.probability > 0.7
        ORDER BY distance 
        LIMIT {search_breadth}
        """
        try:
            result_df = self.bq.query(vs_query).drop_duplicates(subset=["uri"])
        except Exception as e:
            _LOGGER.warning(f"Error in nsfw vector search query: {e}")
            return []
        return result_df.to_dict("records")

    def get_collated_recommendation(
        self, successful_plays, watch_history_uris, num_results=10, user_canister_id=None
    ):  # TODO: also get the feed type ()
        """
        Generates a list of recommended post IDs based on the successful plays and watch history,
        applying weighted sampling based on video likes and watch duration.

        Args:
            successful_plays (list of dict): List of dictionaries containing video play information.
            watch_history_uris (list of str): List of video URIs the user has watched.
            num_results (int, optional): Number of results to return. Defaults to 10.
            user_canister_id (str, optional): The canister ID of the user making the request. Defaults to "test_canister".

        Returns:
            MLFeedResponse: A response containing the recommended feed items.
        """
        sample_uris = (
            self.sample_successful_plays(successful_plays)
            if len(successful_plays) > 0
            else []
        )
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_exploit = executor.submit(
                self.get_score_aware_recommendation,
                sample_uris,
                watch_history_uris,
                num_results,
                user_canister_id,
            )
            future_recency = executor.submit(
                self.get_recency_aware_recommendation,
                sample_uris,
                watch_history_uris,
                num_results,
                user_canister_id,
            )
            future_popular = executor.submit(
                self.get_popular_videos, 
                watch_history_uris, 
                num_results, 
                user_canister_id,
            )
            future_random_recent = executor.submit(
                self.get_random_recent_recommendation,
                sample_uris,
                watch_history_uris,
                num_results,
                user_canister_id,
            )

        exploit_recommendation = future_exploit.result()
        recency_recommendation = future_recency.result()
        popular_recommendation = future_popular.result()
        random_recent_recommendation = future_random_recent.result()

        if self.logging:
            url_template = "https://yral.com/hot-or-not/{canister_id}/{post_id}"
            similar_videos = [url_template.format(canister_id=item["canister_id"], post_id=item["post_id"]) for item in exploit_recommendation]
            print(similar_videos)

        def create_feed_response(feed_items):
            return video_recommendation_pb2.MLFeedResponseV2(
                feed=[
                    video_recommendation_pb2.MLPostItemResponseV2(
                        post_id=item["post_id"], 
                        canister_id=item["canister_id"],
                        nsfw_probability=item.get("nsfw_probability", 0.0),
                        video_id=item.get("video_id", "")
                    )
                    for item in feed_items
                ]
            )

        response_exploitation = [
            {
                "post_id": int(item["post_id"]), 
                "canister_id": item["canister_id"],
                "video_id": item.get("video_id", ""),
                "nsfw_probability": item.get("nsfw_probability", 0.0)
            }
            for item in exploit_recommendation
        ]
        response_exploration = [
            {
                "post_id": int(item["post_id"]), 
                "canister_id": item["canister_id"],
                "video_id": item.get("video_id", ""),
                "nsfw_probability": item.get("nsfw_probability", 0.0)
            }
            for item in popular_recommendation
        ]
        response_recency = [
            {
                "post_id": int(item["post_id"]), 
                "canister_id": item["canister_id"],
                "video_id": item.get("video_id", ""),
                "nsfw_probability": item.get("nsfw_probability", 0.0)
            }
            for item in recency_recommendation
        ]
        response_random_recent = [
            {
                "post_id": int(item["post_id"]), 
                "canister_id": item["canister_id"],
                "video_id": item.get("video_id", ""),
                "nsfw_probability": item.get("nsfw_probability", 0.0)
            }
            for item in random_recent_recommendation
        ]

        required_sample_size = self.sample_size
        current_sample_size = len(successful_plays)

        def calculate_exploit_score(
            len_sample, len_required
        ):  # to be replaced with RL based exploration exploitation
            if len_required == 0:
                return 0
            ratio = len_sample / len_required
            score = max(0, min(70, ratio * 70))
            return score

        exploit_score = calculate_exploit_score(
            current_sample_size, required_sample_size
        )
        exploration_score = 100 - exploit_score

        (
            exploitation_score,
            recency_exploitation_score,
            exploration_score,
            random_recent_score,
        ) = (
            exploit_score / 2,
            exploit_score / 2,
            exploration_score * (7 / 8),
            exploration_score * (1 / 8),
        )

        combined_feed = (
            response_exploitation
            + response_recency
            + response_exploration
            + response_random_recent
        )
        combined_weights = (
            [exploitation_score] * len(response_exploitation)
            + [recency_exploitation_score] * len(response_recency)
            + [exploration_score] * len(response_exploration)
            + [random_recent_score] * len(response_random_recent)
        )
        combined_feed_with_weights = list(zip(combined_feed, combined_weights))

        seen = {}
        for item, weight in combined_feed_with_weights:
            identifier = f"{item['post_id']}_{item['canister_id']}"
            if identifier not in seen or seen[identifier][1] < weight:
                seen[identifier] = (item, weight)

        unique_combined_feed_with_weights = list(seen.values())
        combined_feed, combined_weights = zip(*unique_combined_feed_with_weights)

        sampled_feed = random.choices(
            combined_feed, weights=combined_weights, k=num_results
        )

        # for debugging
        if self.logging:
            _LOGGER.info(f"Length of returned feed: {len(sampled_feed)}")
            
        exploitation_count = sum(
            1 for item in sampled_feed if item in response_exploitation
        )
        recency_count = sum(1 for item in sampled_feed if item in response_recency)
        exploration_count = sum(
            1 for item in sampled_feed if item in response_exploration
        )
        random_recent_count = sum(
            1 for item in sampled_feed if item in response_random_recent
        )

        if self.logging:
            _LOGGER.info(
                f"NSFW feed || Exploitation count: {exploitation_count}, Recency count: {recency_count}, Exploration count: {exploration_count}, Random recent count: {random_recent_count}"
            )

            _LOGGER.info(
                f"NSFW feed || Exploitation weight: {exploitation_score}, Exploration weight: {exploration_score}, Recency weight: {recency_exploitation_score}, Random recent weight: {random_recent_score}"
            )

            _LOGGER.info(f"""NSFW feed || Videos recommended: {len(sampled_feed)}""")
            
        response = create_feed_response(sampled_feed)
        return response


if __name__ == "__main__":

    _LOGGER.setLevel(logging.INFO)
    
    import sys
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("[PID %(process)d] %(message)s")
    handler.setFormatter(formatter)
    _LOGGER.addHandler(handler)

    outer_videos_watched = [
        "gs://yral-videos/cc75ebcdfcd04163bee6fcf37737f8bd.mp4",
        "gs://yral-videos/a8e1035908cc4e6e84f1792f8d655f25.mp4",
        "gs://yral-videos/9072dc569fe24c6d8ed7504d111cd71f.mp4",
        "gs://yral-videos/5054ef5791024da1977b446165aa9fb6.mp4",
        "gs://yral-videos/831fc4a20f974090aa7da3bedc9b0499.mp4",
        "gs://yral-videos/17e4f909dbf14a0b8b13e2b67ea5e54f.mp4",
        "gs://yral-videos/19d5ab6b30914e288db3f8b00dc5ab30.mp4",
        "gs://yral-videos/02b0c85d4da34c9aba1cf48b3b476ce8.mp4",
        "gs://yral-videos/53ec853631a844b48f57e893662daa2c.mp4",
        "gs://yral-videos/b3aac8dad2ef40b6bc987dcda57abd76.mp4",
    ] * 1  # outer prefix for variables that are also used in the logic code

    outer_successful_plays = outer_videos_watched[:10]
    # outer_successful_plays = ["gs://yral-videos/bb13dbff7ee3494bae5bcb7e9309c5fe.mp4"]*5
    outer_filter_responses = [
        (1, "test_canister", "gs://yral-videos/cc75ebcdfcd04163bee6fcf37737f8bd.mp4")
    ]

    # outer_videos_watched = []
    # outer_successful_plays = []
    outer_num_results = 100

    # input_request_parameters

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

    # input requests
    request = video_recommendation_pb2.MLFeedRequest(
        canister_id="test_canister",
        watch_history=watch_history,
        success_history=success_history,
        filter_posts=filter_posts,
        num_results=outer_num_results,
    )

    # process_request
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

    import time

    recommender = NsfwRecommendationV2Deduped()
    start_time = time.time()
    feed = recommender.get_collated_recommendation(
        successful_plays_, outer_watch_history_uris, num_results, user_canister_id
    )
    end_time = time.time()

    _LOGGER.info(
        f"Time required to get the recommendation: {end_time - start_time:.2f} seconds"
    )
    print(
        f"Time required to get the recommendation: {end_time - start_time:.2f} seconds"
    )

    print("Number of videos recommended: ",len(feed.feed))
    for item in feed.feed:
        print(f"https://yral.com/hot-or-not/{item.canister_id}/{item.post_id}", f"NSFW probability: {item.nsfw_probability}", f"Video ID: {item.video_id}")
        print("--------------------------------")
