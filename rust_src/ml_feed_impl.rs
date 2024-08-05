use ml_feed::{FeedRequest, FeedResponse, PostItem};

use ml_feed::ml_feed_server::MlFeed;
use tonic::{Request, Response, Status};

pub mod ml_feed {
    tonic::include_proto!("ml_feed");
    pub(crate) const FILE_DESCRIPTOR_SET: &[u8] =
        tonic::include_file_descriptor_set!("ml_feed_descriptor");
}

#[derive(Default)]
pub struct MLFeedService {}

#[tonic::async_trait]
impl MlFeed for MLFeedService {
    async fn get_feed(
        &self,
        request: Request<FeedRequest>,
    ) -> Result<Response<FeedResponse>, Status> {
        let req = request.into_inner();

        let res = Response::new(FeedResponse {
            feed: vec![
                PostItem {
                    canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
                    post_id: 125,
                },
                PostItem {
                    canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
                    post_id: 124,
                },
                PostItem {
                    canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
                    post_id: 123,
                },
                PostItem {
                    canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
                    post_id: 122,
                },
                PostItem {
                    canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
                    post_id: 121,
                },
                PostItem {
                    canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
                    post_id: 120,
                },
                PostItem {
                    canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
                    post_id: 119,
                },
                PostItem {
                    canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
                    post_id: 118,
                },
                PostItem {
                    canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
                    post_id: 117,
                },
                PostItem {
                    canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
                    post_id: 116,
                },
                PostItem {
                    canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
                    post_id: 115,
                },
                PostItem {
                    canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
                    post_id: 114,
                },
                PostItem {
                    canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
                    post_id: 113,
                },
                PostItem {
                    canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
                    post_id: 112,
                },
                PostItem {
                    canister_id: "vcqbz-sqaaa-aaaag-aesbq-cai".to_string(),
                    post_id: 27,
                },
                PostItem {
                    canister_id: "vcqbz-sqaaa-aaaag-aesbq-cai".to_string(),
                    post_id: 26,
                },
                PostItem {
                    canister_id: "vcqbz-sqaaa-aaaag-aesbq-cai".to_string(),
                    post_id: 25,
                },
                PostItem {
                    canister_id: "vcqbz-sqaaa-aaaag-aesbq-cai".to_string(),
                    post_id: 24,
                },
                PostItem {
                    canister_id: "vcqbz-sqaaa-aaaag-aesbq-cai".to_string(),
                    post_id: 23,
                },
                PostItem {
                    canister_id: "vcqbz-sqaaa-aaaag-aesbq-cai".to_string(),
                    post_id: 22,
                },
                PostItem {
                    canister_id: "vcqbz-sqaaa-aaaag-aesbq-cai".to_string(),
                    post_id: 21,
                },
                PostItem {
                    canister_id: "vcqbz-sqaaa-aaaag-aesbq-cai".to_string(),
                    post_id: 20,
                },
                PostItem {
                    canister_id: "vcqbz-sqaaa-aaaag-aesbq-cai".to_string(),
                    post_id: 19,
                },
                PostItem {
                    canister_id: "vcqbz-sqaaa-aaaag-aesbq-cai".to_string(),
                    post_id: 18,
                },
                PostItem {
                    canister_id: "vcqbz-sqaaa-aaaag-aesbq-cai".to_string(),
                    post_id: 17,
                },
                PostItem {
                    canister_id: "vcqbz-sqaaa-aaaag-aesbq-cai".to_string(),
                    post_id: 16,
                },
                PostItem {
                    canister_id: "vcqbz-sqaaa-aaaag-aesbq-cai".to_string(),
                    post_id: 15,
                },
                PostItem {
                    canister_id: "vcqbz-sqaaa-aaaag-aesbq-cai".to_string(),
                    post_id: 14,
                },
                PostItem {
                    canister_id: "vcqbz-sqaaa-aaaag-aesbq-cai".to_string(),
                    post_id: 13,
                },
                PostItem {
                    canister_id: "vcqbz-sqaaa-aaaag-aesbq-cai".to_string(),
                    post_id: 3,
                },
                PostItem {
                    canister_id: "vcqbz-sqaaa-aaaag-aesbq-cai".to_string(),
                    post_id: 2,
                },
                PostItem {
                    canister_id: "vcqbz-sqaaa-aaaag-aesbq-cai".to_string(),
                    post_id: 1,
                },
            ],
        });

        Ok(res)
    }
}
