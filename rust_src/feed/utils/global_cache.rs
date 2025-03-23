use yral_ml_feed_cache::types::PostItem;

use crate::{
    consts::ML_FEED_PY_SERVER,
    grpc_services::ml_feed_py::{ml_feed_client::MlFeedClient, MlFeedRequest},
};

pub async fn get_global_cache_clean() -> Result<Vec<PostItem>, anyhow::Error> {
    let mut client = match MlFeedClient::connect(
        ML_FEED_PY_SERVER, // http://python_proc.process.yral-ml-feed-server.internal:50059"
    )
    .await
    {
        Ok(client) => client,
        Err(e) => {
            log::error!("Failed to connect to ml_feed_py server: {:?}", e);
            return Err(anyhow::anyhow!("Failed to connect to ml_feed_py server"));
        }
    };

    let request = tonic::Request::new(MlFeedRequest {
        canister_id: "".to_string(),
        watch_history: vec![],
        success_history: vec![],
        filter_posts: vec![],
        num_results: 3000,
    });

    let response = client.get_ml_feed_clean_v1(request).await.map_err(|e| {
        log::error!("Failed to get get_ml_feed_clean_v1 response: {}", e);
        anyhow::anyhow!("Failed to get get_ml_feed_clean_v1 response: {}", e)
    })?;

    let response_obj = response.into_inner();

    let response_items = response_obj
        .feed
        .iter()
        .map(|x| PostItem {
            canister_id: x.canister_id.clone(),
            post_id: x.post_id as u64,
            video_id: "".to_string(),
            nsfw_probability: 0.0,
        })
        .collect::<Vec<PostItem>>();

    Ok(response_items)
}

pub async fn get_global_cache_nsfw() -> Result<Vec<PostItem>, anyhow::Error> {
    let mut client = match MlFeedClient::connect(
        ML_FEED_PY_SERVER, // http://python_proc.process.yral-ml-feed-server.internal:50059"
    )
    .await
    {
        Ok(client) => client,
        Err(e) => {
            log::error!("Failed to connect to ml_feed_py server: {:?}", e);
            return Err(anyhow::anyhow!("Failed to connect to ml_feed_py server"));
        }
    };

    let request = tonic::Request::new(MlFeedRequest {
        canister_id: "".to_string(),
        watch_history: vec![],
        success_history: vec![],
        filter_posts: vec![],
        num_results: 3000,
    });

    let response = client.get_ml_feed_nsfw_v1(request).await.map_err(|e| {
        log::error!("Failed to get get_ml_feed_clean_v1 response: {}", e);
        anyhow::anyhow!("Failed to get get_ml_feed_clean_v1 response: {}", e)
    })?;

    let response_obj = response.into_inner();

    let response_items = response_obj
        .feed
        .iter()
        .map(|x| PostItem {
            canister_id: x.canister_id.clone(),
            post_id: x.post_id as u64,
            video_id: "".to_string(),
            nsfw_probability: 1.0,
        })
        .collect::<Vec<PostItem>>();

    Ok(response_items)
}

pub async fn get_global_cache_mixed() -> Result<Vec<PostItem>, anyhow::Error> {
    let mut client = match MlFeedClient::connect(
        ML_FEED_PY_SERVER, // http://python_proc.process.yral-ml-feed-server.internal:50059"
    )
    .await
    {
        Ok(client) => client,
        Err(e) => {
            log::error!("Failed to connect to ml_feed_py server: {:?}", e);
            return Err(anyhow::anyhow!("Failed to connect to ml_feed_py server"));
        }
    };

    let request = tonic::Request::new(MlFeedRequest {
        canister_id: "".to_string(),
        watch_history: vec![],
        success_history: vec![],
        filter_posts: vec![],
        num_results: 3000,
    });

    let response = client.get_ml_feed_nsfw_v1(request).await.map_err(|e| {
        log::error!("Failed to get get_ml_feed_mixed_v1 response: {}", e);
        anyhow::anyhow!("Failed to get get_ml_feed_mixed_v1 response: {}", e)
    })?;

    let response_obj = response.into_inner();

    let response_items = response_obj
        .feed
        .iter()
        .map(|x| PostItem {
            canister_id: x.canister_id.clone(),
            post_id: x.post_id as u64,
            video_id: "".to_string(),
            nsfw_probability: 1.0,
        })
        .collect::<Vec<PostItem>>();

    Ok(response_items)
}
