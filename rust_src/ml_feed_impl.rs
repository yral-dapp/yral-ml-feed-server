use std::collections::HashSet;
use std::env;
use std::sync::Arc;

use anyhow::anyhow;
use candid::Principal;
use ic_agent::Agent;
use ml_feed::{FeedRequest, FeedResponse, FeedResponseV1, PostItem, PostItemResponse};

use ml_feed::ml_feed_server::MlFeed;
use ml_feed_py::ml_feed_client::MlFeedClient;
use ml_feed_py::{MlFeedRequest, MlFeedResponse};
use off_chain::off_chain_canister_client::OffChainCanisterClient;
use prost::bytes::buf::Limit;
use tonic::metadata::MetadataValue;
use tonic::transport::{Channel, ClientTlsConfig};
use tonic::{Request, Response, Status};

use crate::consts::{ML_FEED_PY_SERVER, OFF_CHAIN_AGENT};
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

pub mod off_chain {
    tonic::include_proto!("offchain_canister");
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
        let limit = req_obj.num_results as usize;
        let canister_id = req_obj.canister_id.clone();

        let mut client = match MlFeedClient::connect(
            ML_FEED_PY_SERVER, // http://python_proc.process.yral-ml-feed-server.internal:50059"
        )
        .await
        {
            Ok(client) => client,
            Err(e) => {
                println!("Failed to connect to ml_feed_py server: {:?}", e);
                return Err(Status::internal("Failed to connect to ml_feed_py server"));
            }
        };

        let request = match get_feed_request_logic(req_obj, &self.shared_state.agent).await {
            Ok(req) => req,
            Err(e) => {
                println!("Failed to create feed request: {:?}", e);
                return Err(Status::internal("Failed to create feed request"));
            }
        };

        let response = client
            .get_ml_feed(request)
            .await
            .map_err(|e| Status::internal(format!("Failed to get ml_feed_py response: {}", e)))?;

        let response_obj = response.into_inner();

        feed_response_logic(response_obj, canister_id, limit).await
    }

    async fn get_feed_v1(
        &self,
        request: Request<FeedRequest>,
    ) -> Result<Response<FeedResponseV1>, Status> {
        Ok(Response::new(FeedResponseV1 { feed: vec![] }))
    }

    async fn get_feed_coldstart(
        &self,
        request: Request<FeedRequest>,
    ) -> Result<Response<FeedResponse>, Status> {
        let req_obj = request.into_inner();
        let limit = req_obj.num_results as usize;
        let canister_id = req_obj.canister_id.clone();

        let mut client = match MlFeedClient::connect(
            ML_FEED_PY_SERVER, // http://python_proc.process.yral-ml-feed-server.internal:50059"
        )
        .await
        {
            Ok(client) => client,
            Err(e) => {
                println!("Failed to connect to ml_feed_py server: {:?}", e);
                return Err(Status::internal("Failed to connect to ml_feed_py server"));
            }
        };

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
            watch_history: vec![],
            success_history: vec![],
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

        Ok(Response::new(FeedResponse {
            feed: response_items,
        }))
    }

    async fn get_feed_clean(
        &self,
        request: Request<FeedRequest>,
    ) -> Result<Response<FeedResponse>, Status> {
        let req_obj = request.into_inner();
        let limit = req_obj.num_results as usize;
        let canister_id = req_obj.canister_id.clone();

        let mut client = match MlFeedClient::connect(
            ML_FEED_PY_SERVER, // http://python_proc.process.yral-ml-feed-server.internal:50059"
        )
        .await
        {
            Ok(client) => client,
            Err(e) => {
                println!("Failed to connect to ml_feed_py server: {:?}", e);
                return Err(Status::internal("Failed to connect to ml_feed_py server"));
            }
        };

        let request = match get_feed_request_logic(req_obj, &self.shared_state.agent).await {
            Ok(req) => req,
            Err(e) => {
                println!("Failed to create feed request: {:?}", e);
                return Err(Status::internal("Failed to create feed request"));
            }
        };

        // println!("request: {:?}", request);

        let response = client
            .get_ml_feed_clean(request)
            .await
            .map_err(|e| Status::internal(format!("Failed to get ml_feed_py response: {}", e)))?;

        let response_obj = response.into_inner();

        feed_response_logic(response_obj, canister_id, limit).await
    }

    async fn get_feed_nsfw(
        &self,
        request: Request<FeedRequest>,
    ) -> Result<Response<FeedResponse>, Status> {
        let req_obj = request.into_inner();
        let limit = req_obj.num_results as usize;
        let canister_id = req_obj.canister_id.clone();

        let mut client = match MlFeedClient::connect(
            ML_FEED_PY_SERVER, // http://python_proc.process.yral-ml-feed-server.internal:50059"
        )
        .await
        {
            Ok(client) => client,
            Err(e) => {
                println!("Failed to connect to ml_feed_py server: {:?}", e);
                return Err(Status::internal("Failed to connect to ml_feed_py server"));
            }
        };

        let request = match get_feed_request_logic(req_obj, &self.shared_state.agent).await {
            Ok(req) => req,
            Err(e) => {
                println!("Failed to create feed request: {:?}", e);
                return Err(Status::internal("Failed to create feed request"));
            }
        };

        let response = client
            .get_ml_feed_nsfw(request)
            .await
            .map_err(|e| Status::internal(format!("Failed to get ml_feed_py response: {}", e)))?;

        let response_obj = response.into_inner();

        feed_response_logic(response_obj, canister_id, limit).await
    }
}

pub async fn get_feed_request_logic(
    req_obj: FeedRequest,
    ic_agent: &Agent,
) -> Result<Request<MlFeedRequest>, anyhow::Error> {
    let limit = req_obj.num_results;

    // println!("get_feed request: {:?}", req_obj);

    let canister_id = req_obj.canister_id.clone();
    let canister_id_principal = Principal::from_text(&canister_id).unwrap();

    let user_canister = canister::individual_user(ic_agent, canister_id_principal);

    let watch_history = canister::get_watch_history(&user_canister)
        .await
        .map_or(vec![], |x| x);
    let success_history = canister::get_success_history(&user_canister)
        .await
        .map_or(vec![], |x| x);

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

    Ok(tonic::Request::new(MlFeedRequest {
        canister_id: req_obj.canister_id,
        watch_history: watch_history_items,
        success_history: success_history_items,
        filter_posts: filter_items,
        num_results: req_obj.num_results + 15,
    }))
}

pub async fn feed_response_logic(
    response_obj: MlFeedResponse,
    canister_id: String,
    limit: usize,
) -> Result<Response<FeedResponse>, Status> {
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
    let mut response_items = response_items
        .into_iter()
        .filter(|e| seen.insert((e.canister_id.clone(), e.post_id)))
        .collect::<Vec<PostItemResponse>>();

    // get last 15 items from response_items without split_off
    let at = response_items.len().saturating_sub(15);
    let mut response_items1 = response_items.iter().skip(at).cloned().collect::<Vec<_>>();
    tokio::spawn(async move {
        response_items1.reverse();
        send_to_offchain(canister_id, response_items1).await;
    });

    // take first limit items
    response_items.truncate(limit as usize);

    Ok(Response::new(FeedResponse {
        feed: response_items,
    }))
}

pub async fn send_to_offchain(canister_id_principal_str: String, items: Vec<PostItemResponse>) {
    let tls_config = ClientTlsConfig::new().with_webpki_roots();
    let channel = Channel::from_static(OFF_CHAIN_AGENT)
        .tls_config(tls_config)
        .expect("Couldn't update TLS config for off-chain agent")
        .connect()
        .await
        .expect("channel creation failed");

    let grpc_offchain_token =
        env::var("GRPC_OFF_CHAIN_JWT_TOKEN").expect("GRPC_OFF_CHAIN_JWT_TOKEN must be set");

    let token: MetadataValue<_> = format!("Bearer {}", grpc_offchain_token)
        .parse()
        .expect("invalid metadata value");

    let mut client =
        OffChainCanisterClient::with_interceptor(channel, move |mut req: Request<()>| {
            req.metadata_mut().insert("authorization", token.clone());
            Ok(req)
        });

    let offchain_items = items
        .into_iter()
        .map(|x| off_chain::MlFeedCacheItem {
            post_id: x.post_id as u64,
            canister_id: x.canister_id,
            video_id: "".to_string(),
            creator_principal_id: "".to_string(),
        })
        .collect::<Vec<off_chain::MlFeedCacheItem>>();

    let request = tonic::Request::new(off_chain::UpdateMlFeedCacheRequest {
        user_canister_id: canister_id_principal_str,
        items: offchain_items,
    });

    let response = client.update_ml_feed_cache(request).await.map_err(|e| {
        Status::internal(format!(
            "Failed to get update_ml_feed_cache response: {}",
            e
        ))
    });

    match response {
        Ok(_) => (),
        Err(e) => println!("Failed to get update_ml_feed_cache response: {}", e),
    }
}
