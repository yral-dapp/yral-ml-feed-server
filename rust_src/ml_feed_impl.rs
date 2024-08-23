use std::collections::HashSet;
use std::sync::Arc;

use candid::Principal;
use ml_feed::{FeedRequest, FeedResponse, PostItem, PostItemResponse};

use ml_feed::ml_feed_server::MlFeed;
use ml_feed_py::ml_feed_client::MlFeedClient;
use ml_feed_py::MlFeedRequest;
use tonic::{Request, Response, Status};

use crate::consts::ML_FEED_PY_SERVER;
use crate::utils::{to_rfc3339, to_rfc3339_did_systemtime};
use crate::{canister, AppState};

pub mod ml_feed {
    tonic::include_proto!("ml_feed");
    pub(crate) const FILE_DESCRIPTOR_SET: &[u8] =
        tonic::include_file_descriptor_set!("ml_feed_descriptor");
}

pub mod ml_feed_py {
    tonic::include_proto!("ml_feed_py");
    pub(crate) const FILE_DESCRIPTOR_SET: &[u8] =
        tonic::include_file_descriptor_set!("ml_feed_py_descriptor");
}

pub struct MLFeedService {
    pub shared_state: Arc<AppState>,
}

#[tonic::async_trait]
impl MlFeed for MLFeedService {
    async fn get_feed(
        &self,
        request: Request<FeedRequest>,
    ) -> Result<Response<FeedResponse>, Status> {
        let req_obj = request.into_inner();
        let limit = req_obj.num_results;

        // println!("get_feed request: {:?}", req_obj);

        let canister_id = req_obj.canister_id.clone();
        let canister_id_principal = Principal::from_text(&canister_id).unwrap();

        let user_canister =
            canister::individual_user(&self.shared_state.agent, canister_id_principal);

        let watch_history = canister::get_watch_history(&user_canister)
            .await
            .map_or(vec![], |x| x);
        let success_history = canister::get_success_history(&user_canister)
            .await
            .map_or(vec![], |x| x);

        let mut client = match MlFeedClient::connect(
            "http://python_proc.process.yral-ml-feed-server.internal:50059",
        )
        .await
        {
            Ok(client) => client,
            Err(e) => {
                println!("Failed to connect to ml_feed_py server: {:?}", e);
                return Err(Status::internal("Failed to connect to ml_feed_py server"));
            }
        };

        let watch_history_items = watch_history
            .iter()
            .map(|x| ml_feed_py::WatchHistoryItem {
                post_id: x.post_id as u32,
                canister_id: x.publisher_canister_id.to_text(),
                video_id: format!("gs://yral-videos/{}.mp4", x.cf_video_id.clone()),
                percent_watched: x.percentage_watched,
                timestamp: to_rfc3339_did_systemtime(&x.viewed_at),
            })
            .collect::<Vec<ml_feed_py::WatchHistoryItem>>();

        // println!("watch_history_items: {:?}", watch_history_items);

        let success_history_items = success_history
            .iter()
            .map(|x| ml_feed_py::SuccessHistoryItem {
                post_id: x.post_id as u32,
                canister_id: x.publisher_canister_id.to_text(),
                video_id: format!("gs://yral-videos/{}.mp4", x.cf_video_id.clone()),
                timestamp: to_rfc3339_did_systemtime(&x.interacted_at),
                item_type: x.item_type.clone(),
                percent_watched: x.percentage_watched,
            })
            .collect::<Vec<ml_feed_py::SuccessHistoryItem>>();

        // println!("success_history_items: {:?}", success_history_items);

        let filter_items = req_obj
            .filter_posts
            .iter()
            .map(|x| ml_feed_py::MlPostItem {
                canister_id: x.canister_id.clone(),
                post_id: x.post_id as u32,
                video_id: format!("gs://yral-videos/{}.mp4", x.video_id.clone()),
            })
            .collect::<Vec<ml_feed_py::MlPostItem>>();

        let request = tonic::Request::new(MlFeedRequest {
            canister_id: req_obj.canister_id,
            watch_history: watch_history_items,
            success_history: success_history_items,
            filter_posts: filter_items,
            num_results: req_obj.num_results,
        });

        let response = client
            .get_ml_feed(request)
            .await
            .map_err(|e| Status::internal(format!("Failed to get ml_feed_py response: {}", e)))?;

        let response_obj = response.into_inner();

        let response_items = response_obj
            .feed
            .iter()
            .map(|x| PostItemResponse {
                canister_id: x.canister_id.clone(),
                post_id: x.post_id as u32,
            })
            .collect::<Vec<PostItemResponse>>();

        // filter out duplicates
        let mut seen = HashSet::new();
        let response_items = response_items
            .into_iter()
            .filter(|e| seen.insert((e.canister_id.clone(), e.post_id)))
            .collect::<Vec<PostItemResponse>>();

        return Ok(Response::new(FeedResponse {
            feed: response_items,
        }));

        // let res = vec![
        //     PostItemResponse {
        //         canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
        //         post_id: 125,
        //     },
        //     PostItemResponse {
        //         canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
        //         post_id: 124,
        //     },
        //     PostItemResponse {
        //         canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
        //         post_id: 123,
        //     },
        //     PostItemResponse {
        //         canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
        //         post_id: 122,
        //     },
        //     PostItemResponse {
        //         canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
        //         post_id: 121,
        //     },
        //     PostItemResponse {
        //         canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
        //         post_id: 120,
        //     },
        //     PostItemResponse {
        //         canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
        //         post_id: 119,
        //     },
        //     PostItemResponse {
        //         canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
        //         post_id: 118,
        //     },
        //     PostItemResponse {
        //         canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
        //         post_id: 117,
        //     },
        //     PostItemResponse {
        //         canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
        //         post_id: 116,
        //     },
        //     PostItemResponse {
        //         canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
        //         post_id: 115,
        //     },
        //     PostItemResponse {
        //         canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
        //         post_id: 114,
        //     },
        //     PostItemResponse {
        //         canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
        //         post_id: 113,
        //     },
        //     PostItemResponse {
        //         canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
        //         post_id: 112,
        //     },
        //     PostItemResponse {
        //         canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
        //         post_id: 111,
        //     },
        //     PostItemResponse {
        //         canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
        //         post_id: 110,
        //     },
        //     PostItemResponse {
        //         canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
        //         post_id: 109,
        //     },
        //     PostItemResponse {
        //         canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
        //         post_id: 108,
        //     },
        //     PostItemResponse {
        //         canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
        //         post_id: 107,
        //     },
        //     PostItemResponse {
        //         canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
        //         post_id: 106,
        //     },
        //     PostItemResponse {
        //         canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
        //         post_id: 105,
        //     },
        //     PostItemResponse {
        //         canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
        //         post_id: 104,
        //     },
        //     PostItemResponse {
        //         canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
        //         post_id: 103,
        //     },
        //     PostItemResponse {
        //         canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
        //         post_id: 102,
        //     },
        //     PostItemResponse {
        //         canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
        //         post_id: 101,
        //     },
        //     PostItemResponse {
        //         canister_id: "76qol-iiaaa-aaaak-qelkq-cai".to_string(),
        //         post_id: 100,
        //     },
        // ];

        // let res_limited = res
        //     .into_iter()
        //     .take(limit as usize)
        //     .collect::<Vec<PostItemResponse>>();

        // Ok(Response::new(FeedResponse { feed: res_limited }))
    }
}
