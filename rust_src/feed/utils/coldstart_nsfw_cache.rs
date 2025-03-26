use std::collections::HashSet;

use anyhow::Ok;
use rand::Rng;
use yral_ml_feed_cache::{
    consts::{
        GLOBAL_CACHE_NSFW_KEY, MAX_GLOBAL_CACHE_LEN, MAX_WATCH_HISTORY_CACHE_LEN,
        USER_CACHE_NSFW_SUFFIX, USER_WATCH_HISTORY_NSFW_SUFFIX,
    },
    types::PostItem,
    MLFeedCacheState,
};

use super::get_shuffled_limit_list;

pub async fn get_coldstart_nsfw_cache_noinput_impl(
    ml_feed_cache: MLFeedCacheState,
) -> Result<Vec<PostItem>, anyhow::Error> {
    let num_posts_in_cache = ml_feed_cache
        .get_cache_items_len(GLOBAL_CACHE_NSFW_KEY)
        .await
        .map_err(|e| anyhow::anyhow!("Failed to get num posts in cache: {}", e))?;

    let post_index = rand::rng().random_range(0..num_posts_in_cache);
    let feed = ml_feed_cache
        .get_cache_items(GLOBAL_CACHE_NSFW_KEY, post_index, post_index + 1)
        .await
        .map_err(|e| anyhow::anyhow!("Failed to get post from cache: {}", e))?;

    Ok(feed)
}

pub async fn get_coldstart_nsfw_cache_noinput_user_impl(
    ml_feed_cache: MLFeedCacheState,
    canister_id: String,
) -> Result<Vec<PostItem>, anyhow::Error> {
    let num_posts_in_cache = ml_feed_cache
        .get_cache_items_len(&format!("{}{}", canister_id, USER_CACHE_NSFW_SUFFIX))
        .await
        .map_err(|e| anyhow::anyhow!("Failed to get num posts in cache: {}", e))?;

    if num_posts_in_cache == 0 {
        return get_coldstart_nsfw_cache_noinput_impl(ml_feed_cache).await;
    }

    let post_index = rand::rng().random_range(0..num_posts_in_cache);
    let feed = ml_feed_cache
        .get_cache_items(
            &format!("{}{}", canister_id, USER_CACHE_NSFW_SUFFIX),
            post_index,
            post_index + 1,
        )
        .await
        .map_err(|e| anyhow::anyhow!("Failed to get post from cache: {}", e))?;

    Ok(feed)
}

pub async fn get_coldstart_nsfw_cache_input_impl(
    ml_feed_cache: MLFeedCacheState,
    num_results: u32,
) -> Result<Vec<PostItem>, anyhow::Error> {
    let global_cache_nsfw_feed = ml_feed_cache
        .get_cache_items(GLOBAL_CACHE_NSFW_KEY, 0, MAX_GLOBAL_CACHE_LEN)
        .await
        .map_err(|e| anyhow::anyhow!("Failed to get global cache nsfw feed: {}", e))?;

    Ok(get_shuffled_limit_list(global_cache_nsfw_feed, num_results as usize).await)
}

pub async fn get_coldstart_nsfw_cache_input_user_impl(
    ml_feed_cache: MLFeedCacheState,
    canister_id: String,
    num_results: u32,
    filter_results: Vec<PostItem>,
) -> Result<Vec<PostItem>, anyhow::Error> {
    let num_posts_in_cache = ml_feed_cache
        .get_cache_items_len(&format!("{}{}", canister_id, USER_CACHE_NSFW_SUFFIX))
        .await
        .map_err(|e| anyhow::anyhow!("Failed to get num posts in cache: {}", e))?;

    if num_posts_in_cache == 0 {
        return get_coldstart_nsfw_cache_input_impl(ml_feed_cache, num_results).await;
    }

    let watch_history = ml_feed_cache
        .get_history_items(
            &format!("{}{}", canister_id, USER_WATCH_HISTORY_NSFW_SUFFIX),
            0,
            MAX_WATCH_HISTORY_CACHE_LEN,
        )
        .await
        .map_err(|e| anyhow::anyhow!("Failed to get watch history: {}", e))?;

    // create a set of PostItems from watch_history
    let mut watch_history_set = watch_history
        .iter()
        .map(|item| PostItem {
            canister_id: item.canister_id.clone(),
            post_id: item.post_id as u64,
            video_id: item.video_id.clone(),
            nsfw_probability: item.nsfw_probability,
        })
        .collect::<HashSet<PostItem>>();

    for item in filter_results {
        watch_history_set.insert(item);
    }

    let user_cache_items = ml_feed_cache
        .get_cache_items(
            &format!("{}{}", canister_id, USER_CACHE_NSFW_SUFFIX),
            0,
            num_posts_in_cache,
        )
        .await
        .map_err(|e| anyhow::anyhow!("Failed to get user cache items: {}", e))?;

    let mut feed = Vec::new();
    for item in user_cache_items {
        if !watch_history_set.contains(&item) {
            feed.push(item);
        }
    }

    Ok(get_shuffled_limit_list(feed, num_results as usize).await)
}
