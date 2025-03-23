use std::{net::SocketAddr, sync::Arc, time::Duration};

use anyhow::Result;
use app_state::AppState;
use axum::{routing::get, Router};
use canister::init_agent;
use consts::ML_FEED_PY_SERVER;
use env_logger::{Builder, Target};
use grpc_services::{
    ml_feed::ml_feed_server::MlFeedServer, ml_feed_py::ml_feed_client::MlFeedClient,
};
use http::{header::CONTENT_TYPE, StatusCode};
use ic_agent::Agent;
use log::LevelFilter;
use ml_feed_impl::MLFeedService;
use tonic::codegen::http::header::HeaderName;
use tonic::transport::Server;
use tonic_web::GrpcWebLayer;
use tower::{make::Shared, steer::Steer};
use tower_http::cors::{AllowOrigin, CorsLayer};
use utoipa::{openapi, OpenApi};
use utoipa_axum::router::OpenApiRouter;
use utoipa_swagger_ui::SwaggerUi;

pub mod app_state;
pub mod canister;
pub mod consts;
pub mod error;
pub mod feed;
pub mod grpc_services;
pub mod ml_feed_impl;
pub mod utils;

const DEFAULT_MAX_AGE: Duration = Duration::from_secs(24 * 60 * 60);
const DEFAULT_EXPOSED_HEADERS: [&str; 3] =
    ["grpc-status", "grpc-message", "grpc-status-details-bin"];
const DEFAULT_ALLOW_HEADERS: [&str; 4] =
    ["x-grpc-web", "content-type", "x-user-agent", "grpc-timeout"];

#[tokio::main]
async fn main() -> Result<()> {
    #[derive(OpenApi)]
    #[openapi(
        tags(
            (name = "ML_FEED", description = "ML Feed API")
        )
    )]
    struct ApiDoc;

    Builder::new()
        .filter_level(LevelFilter::Info)
        .target(Target::Stdout)
        .init();

    let app_state = Arc::new(AppState::new().await);

    let (router, api) = OpenApiRouter::with_openapi(ApiDoc::openapi())
        .nest("/api/v1/feed", feed::feed_router(app_state.clone()))
        .split_for_parts();

    let router =
        router.merge(SwaggerUi::new("/swagger-ui").url("/api-docs/openapi.json", api.clone()));

    let mlfeed_service = MLFeedService {
        shared_state: app_state.clone(),
    };
    let mlfeed_server = MlFeedServer::new(mlfeed_service);

    let http = Router::new()
        .route("/healthz", get(health_handler))
        .nest_service("/", router)
        .layer(CorsLayer::permissive())
        .with_state(app_state.clone());

    let grpc_axum = Server::builder()
        .accept_http1(true)
        .add_service(tonic_web::enable(mlfeed_server))
        .into_service()
        .into_axum_router();

    let http_grpc = Steer::new(
        vec![http, grpc_axum],
        |req: &axum::extract::Request, _svcs: &[_]| {
            if req.headers().get(CONTENT_TYPE).map(|v| v.as_bytes()) != Some(b"application/grpc") {
                0
            } else {
                1
            }
        },
    );

    let addr = SocketAddr::from(([0, 0, 0, 0, 0, 0, 0, 0], 50051));
    let listener = tokio::net::TcpListener::bind(&addr).await.unwrap();

    log::info!("listening on {}", addr);

    axum::serve(listener, Shared::new(http_grpc)).await.unwrap();

    // #[cfg(not(feature = "local-bin"))]
    // {
    //     Server::builder()
    //         .add_service(tonic_web::enable(mlfeed_server))
    //         .serve(addr)
    //         .await?;
    // }

    // #[cfg(feature = "local-bin")]
    // {
    //     Server::builder()
    //         .accept_http1(true)
    //         .layer(
    //             CorsLayer::new()
    //                 .allow_origin(AllowOrigin::mirror_request())
    //                 .allow_credentials(true)
    //                 .max_age(DEFAULT_MAX_AGE)
    //                 .expose_headers(
    //                     DEFAULT_EXPOSED_HEADERS
    //                         .iter()
    //                         .cloned()
    //                         .map(HeaderName::from_static)
    //                         .collect::<Vec<HeaderName>>(),
    //                 )
    //                 .allow_headers(
    //                     DEFAULT_ALLOW_HEADERS
    //                         .iter()
    //                         .cloned()
    //                         .map(HeaderName::from_static)
    //                         .collect::<Vec<HeaderName>>(),
    //                 ),
    //         )
    //         .layer(GrpcWebLayer::new())
    //         .add_service(mlfeed_server)
    //         .serve(addr)
    //         .await?;
    // }

    Ok(())
}

async fn health_handler() -> (StatusCode, &'static str) {
    log::info!("Health check");
    log::warn!("Health check");
    log::error!("Health check");

    (StatusCode::OK, "OK")
}
