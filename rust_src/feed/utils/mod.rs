use rand::seq::SliceRandom;
use yral_ml_feed_cache::types::PostItem;

pub mod coldstart_clean_cache;
pub mod coldstart_mixed_cache;
pub mod coldstart_nsfw_cache;
pub mod global_cache;
pub mod ml_feed;

pub async fn get_shuffled_limit_list(list: Vec<PostItem>, limit: usize) -> Vec<PostItem> {
    let mut rng = rand::rng();
    let mut indices = (0..list.len()).collect::<Vec<_>>();
    indices.shuffle(&mut rng);
    indices
        .into_iter()
        .take(limit)
        .map(|i| list[i].clone())
        .collect()
}
