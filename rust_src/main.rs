use std::{net::SocketAddr, sync::Arc, time::Duration};

use anyhow::Result;
use canister::init_agent;
use consts::ML_FEED_PY_SERVER;
use http::header::HeaderName;
use ic_agent::Agent;
use ml_feed_impl::{
    ml_feed::ml_feed_server::MlFeedServer, ml_feed_py::ml_feed_client::MlFeedClient, MLFeedService,
};
use tonic::transport::Server;
use tonic_web::GrpcWebLayer;
use tower_http::cors::{AllowOrigin, CorsLayer};

pub mod canister;
pub mod consts;
pub mod error;
pub mod ml_feed_impl;
pub mod utils;

const DEFAULT_MAX_AGE: Duration = Duration::from_secs(24 * 60 * 60);
const DEFAULT_EXPOSED_HEADERS: [&str; 3] =
    ["grpc-status", "grpc-message", "grpc-status-details-bin"];
const DEFAULT_ALLOW_HEADERS: [&str; 4] =
    ["x-grpc-web", "content-type", "x-user-agent", "grpc-timeout"];

pub struct AppState {
    pub agent: Agent,
}

impl AppState {
    pub async fn new() -> Self {
        AppState {
            agent: init_agent().await,
        }
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    let addr = SocketAddr::from(([0, 0, 0, 0, 0, 0, 0, 0], 50051));

    let app_state = AppState::new().await;

    let mlfeed_service = MLFeedService {
        shared_state: Arc::new(app_state),
    };
    let mlfeed_server = MlFeedServer::new(mlfeed_service);

    println!("MlFeedServer listening on {}", addr);

    Server::builder()
        .add_service(tonic_web::enable(mlfeed_server))
        .serve(addr)
        .await?;

    // Server::builder()
    //     .accept_http1(true)
    //     .layer(
    //         CorsLayer::new()
    //             .allow_origin(AllowOrigin::mirror_request())
    //             .allow_credentials(true)
    //             .max_age(DEFAULT_MAX_AGE)
    //             .expose_headers(
    //                 DEFAULT_EXPOSED_HEADERS
    //                     .iter()
    //                     .cloned()
    //                     .map(HeaderName::from_static)
    //                     .collect::<Vec<HeaderName>>(),
    //             )
    //             .allow_headers(
    //                 DEFAULT_ALLOW_HEADERS
    //                     .iter()
    //                     .cloned()
    //                     .map(HeaderName::from_static)
    //                     .collect::<Vec<HeaderName>>(),
    //             ),
    //     )
    //     .layer(GrpcWebLayer::new())
    //     .add_service(mlfeed_server)
    //     .serve(addr)
    //     .await?;

    Ok(())
}
