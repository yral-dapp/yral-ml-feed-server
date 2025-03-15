"""BigQuery table constants for recommendation service."""

PROJECT_ID = "hot-or-not-feed-intelligence"
DATASET = "yral_ds"
STAGE_PROJECT_ID = "jay-dhanwant-experiments"
STAGE_DATASET = "stage_tables"

use_stage = False  # TODO: stage change book mark

if not use_stage:
    # Fully qualified table names
    VIDEO_EMBEDDINGS_TABLE = f"`{DATASET}.video_embeddings`"
    GLOBAL_POPULAR_VIDEOS_TABLE = f"`{PROJECT_ID}.{DATASET}.global_popular_videos_l7d`"
    VIDEO_METADATA_TABLE = f"`{PROJECT_ID}.{DATASET}.video_metadata`"
    VIDEO_INDEX_TABLE = f"`{PROJECT_ID}.{DATASET}.video_index`"
    REPORT_VIDEO_TABLE = f"`{PROJECT_ID}.{DATASET}.ml_feed_reports`"
    VIDEO_NSFW_TABLE = f"`{DATASET}.video_nsfw_agg`"

else:
    # Stage table names
    VIDEO_EMBEDDINGS_TABLE = (
        f"`{STAGE_PROJECT_ID}.{STAGE_DATASET}.stage_video_embeddings`"
    )
    GLOBAL_POPULAR_VIDEOS_TABLE = (
        f"`{STAGE_PROJECT_ID}.{STAGE_DATASET}.stage_global_popular_videos`"
    )
    VIDEO_METADATA_TABLE = f"`{STAGE_PROJECT_ID}.{STAGE_DATASET}.stage_video_metadata`"
    VIDEO_INDEX_TABLE = f"`{STAGE_PROJECT_ID}.{STAGE_DATASET}.stage_video_index`"
    # STAGE_TOKEN_METADATA_TABLE = f"`{STAGE_PROJECT_ID}.{STAGE_DATASET}.stage_token_metadata_v1`"
