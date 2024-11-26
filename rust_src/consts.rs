#[cfg(feature = "local-bin")]
pub const ML_FEED_PY_SERVER: &str = "http://localhost:50059"; //"http://python_proc.process.yral-ml-feed-server.internal:50059";

#[cfg(not(feature = "local-bin"))]
pub const ML_FEED_PY_SERVER: &str = "http://python_proc.process.yral-ml-feed-server.internal:50059";

#[cfg(feature = "local-bin")]
pub const OFF_CHAIN_AGENT: &str = "https://pr-91-yral-dapp-off-chain-agent.fly.dev:443";

#[cfg(not(feature = "local-bin"))]
pub const OFF_CHAIN_AGENT: &str = "https://icp-off-chain-agent.fly.dev:443";
