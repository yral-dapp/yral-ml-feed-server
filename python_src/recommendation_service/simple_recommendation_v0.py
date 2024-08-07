from config import Config
from utils.upstash_utils import UpstashUtils
from concurrent.futures import ThreadPoolExecutor
from utils.bigquery_utils import BigQueryClient
from ast import literal_eval
import logging
_LOGGER = logging.getLogger(__name__)

class SimpleRecommendationV0:
    def __init__(self):
        cfg = Config()
        self.bq = BigQueryClient()
        self.upstash_db = UpstashUtils()
        ### hyper-parameters
        self.sample_size = 10 # number of successful plays to sample
        self.video_bucket_name = cfg.get('video_bucket_name')


    def fetch_embeddings(self, uri_list):
        """
        Fetches embeddings for the given list of URIs from BigQuery.

        Args:
            uri_list (list): A list of URIs for which to fetch embeddings.

        Returns:
            pandas.DataFrame: A DataFrame containing the embeddings.
        """
        query = f"""
        SELECT uri, ml_generate_embedding_result, metadata
        FROM `yral_ds.video_embeddings`
        WHERE uri IN UNNEST({uri_list})
        """
        return self.bq.query(query)
    
    def fetch_relevant_id(self, vector, watch_history, num_results):
        filter_query = "uri not in (" + ",".join([f'"{uri}"' for uri in watch_history]) + ")"
        results = self.upstash_db.query(vector, top_k=num_results, include_metadata=True, filter=filter_query)
        exploit_ids = [{'video_uri': result.id, 'canister_id': result.metadata['canister_id'], 'post_id': result.metadata['post_id']} for result in results]
        return exploit_ids
        
    def fetch_relevant_ids(self, vector_to_query, watch_history, num_results=10):
        result = []
        with ThreadPoolExecutor(max_workers=len(vector_to_query)) as executor:
            futures = [executor.submit(self.fetch_relevant_id, vector, watch_history=watch_history, num_results=num_results) for vector in vector_to_query]
            result = []
            for future in futures:
                relevant_ids = future.result()
                result.extend(relevant_ids)
        return result
    
    # def get_recommendation(self, successful_plays, watch_history):
    #     """
    #     Generates a list of recommended post IDs based on the successful plays and watch history.

    #     This function serves as the entry point for generating recommendations. It first fetches
    #     embeddings for the successful plays, filters out any embeddings of incorrect size, and then
    #     samples a subset of these embeddings. It queries the Upstash vector database with these
    #     embeddings to find relevant post IDs that are not in the user's watch history.

    #     Args:
    #         successful_plays (list of str): A list of URIs representing the videos that have been successfully played.
    #         watch_history (list of str): A list of URIs representing the user's watch history.

    #     Returns:
    #         list of dict: A list of dictionaries, where each dictionary contains 'canister_id' and 'post_id'
    #                       keys corresponding to the recommended posts. For example:
    #                       [{'canister_id': '123', 'post_id': '456'}, ...]

    #     """
    #     vdf = self.fetch_embeddings(successful_plays) # video-dataframe
    #     vdf = vdf[vdf.ml_generate_embedding_result.apply(lambda x: len(x))==1408]
    #     sample_vdf = vdf if len(vdf) < self.sample_size else vdf.sample(self.sample_size, random_state=None) # to be replaced with better logic once likes and watch duration is available 
    #     vector_to_query = sample_vdf.ml_generate_embedding_result.tolist()
    #     relevant_ids = self.fetch_relevant_ids(vector_to_query, watch_history)
    #     return relevant_ids
    
    def get_popular_videos(self, watch_history_uris, num_results):
        # Construct the SQL query
        video_ids = [uri.split('/')[-1].split('.')[0] for uri in watch_history_uris] # the script would break if the format is not .mp4
        watched_video_ids = ', '.join(f"'{video_id}'" for video_id in video_ids)
        if watched_video_ids != "":
            query = f"""
            SELECT video_id, global_popularity_score
            FROM `hot-or-not-feed-intelligence.yral_ds.global_popular_videos_l7d`
            WHERE video_id NOT IN ({watched_video_ids})
            ORDER BY global_popularity_score DESC
            LIMIT {int(3*num_results)}
            """
        else:
            query = f"""
            SELECT video_id, global_popularity_score
            FROM `hot-or-not-feed-intelligence.yral_ds.global_popular_videos_l7d`
            ORDER BY global_popularity_score DESC
            LIMIT {int(3*num_results)}
            """
        rdf = self.bq.query(query) # rdf - recent videos data frame 
        video_ids = rdf['video_id'].tolist()

        if not len(video_ids):
            return []
        
        video_ids_string = ', '.join(f'"{video_id}"' for video_id in video_ids)
        
        fetch_post_ids = f"""
        SELECT
        video_id, post_id, canister_id
        FROM `hot-or-not-feed-intelligence.yral_ds.video_metadata`
        WHERE video_id IN ({video_ids_string})
        """

        mdf = self.bq.query(fetch_post_ids) # mdf - metadata dataframe 
        mdf = mdf[(mdf.post_id.isna() == False) & (mdf.canister_id.isna() == False)]
        _LOGGER.info([f"gs://yral-videos/{i}.mp4" for i in mdf.video_id.tolist()])
        return mdf['post_id canister_id'.split()].to_dict('records')
    
    def get_score_aware_recommendation(self, successful_plays, watch_history, num_results=10):
        """
        Generates a list of recommended post IDs based on the successful plays and watch history,
        applying weighted sampling based on video likes and watch duration.

        Args:
            successful_plays (list of dict): A list of dictionaries where each dictionary contains
                                             'video_uri', 'item_type' (either 'video_duration_watched' or 'like_video'),
                                             and 'percent_watched' (a float representing the percentage of the video watched).
            watch_history (list of str): A list of URIs representing the user's watch history.

        Returns:
            list of dict: A list of dictionaries, where each dictionary contains 'canister_id' and 'post_id'
                          keys corresponding to the recommended posts.
        """
        vdf = self.fetch_embeddings([play['video_uri'] for play in successful_plays])
        if not len(successful_plays):
            return []

        scores = {}
        for play in successful_plays:
            like_score = 1 if play['item_type'] == 'like_video' else 0
            watch_duration_score = play['percent_watched'] / 100
            score = (like_score + watch_duration_score) / 2
            scores[play['video_uri']] = score
        vdf['scores'] = vdf.uri.map(scores)

        vdf = vdf[vdf.ml_generate_embedding_result.apply(lambda x: len(x)) == 1408]
        scores = vdf.scores.tolist()

        sample_size = min(len(vdf), self.sample_size)
        if scores:
            sample_vdf = vdf.sample(n=sample_size, weights=scores)
        else:
            sample_vdf = vdf.sample(n=sample_size)

        vector_to_query = sample_vdf.ml_generate_embedding_result.tolist()
        relevant_ids = self.fetch_relevant_ids(vector_to_query, watch_history, num_results=num_results)

        return relevant_ids

        
    


if __name__ == '__main__':
    import time
    start_time = time.time()

    videos_watched = ['gs://yral-videos/cc75ebcdfcd04163bee6fcf37737f8bd.mp4',
    'gs://yral-videos/a8e1035908cc4e6e84f1792f8d655f25.mp4',
    'gs://yral-videos/9072dc569fe24c6d8ed7504d111cd71f.mp4',
    'gs://yral-videos/5054ef5791024da1977b446165aa9fb6.mp4',
    'gs://yral-videos/831fc4a20f974090aa7da3bedc9b0499.mp4',
    'gs://yral-videos/17e4f909dbf14a0b8b13e2b67ea5e54f.mp4',
    'gs://yral-videos/19d5ab6b30914e288db3f8b00dc5ab30.mp4',
    'gs://yral-videos/02b0c85d4da34c9aba1cf48b3b476ce8.mp4',
    'gs://yral-videos/53ec853631a844b48f57e893662daa2c.mp4',
    'gs://yral-videos/b3aac8dad2ef40b6bc987dcda57abd76.mp4']

    rec = SimpleRecommendationV0()
    successful_plays = videos_watched[:6]
    result_exploitation = rec.get_recommendation(successful_plays=successful_plays, watch_history=videos_watched, num_results=10)
    result_exploration = rec.get_popular_videos(watch_history_uris=videos_watched, num_results=10)
    end_time = time.time()
    time_taken = end_time - start_time
    print(f"Time taken: {time_taken:.2f} seconds")
    print(f"Exploitation: {len(result_exploitation)}")
    print(result_exploitation)
    print(f"Exploration: {len(result_exploration)}")
    print(result_exploration)

        