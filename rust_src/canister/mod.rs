#[allow(clippy::all)]
mod generated;

use anyhow::Result;
use candid::Principal;
pub use generated::*;
use ic_agent::Agent;
use individual_user_template::{
    IndividualUserTemplate, Result10, Result12, SuccessHistoryItemV1, WatchHistoryItem,
};

pub async fn init_agent() -> Agent {
    let agent = Agent::builder()
        .with_url("https://ic0.app")
        .build()
        .unwrap();

    agent
}

pub fn individual_user(agent: &Agent, user_canister: Principal) -> IndividualUserTemplate<'_> {
    IndividualUserTemplate(user_canister, agent)
}

pub async fn get_watch_history(
    individual_user_canister: &IndividualUserTemplate<'_>,
) -> Result<Vec<WatchHistoryItem>> {
    match individual_user_canister.get_watch_history().await? {
        Result12::Ok(watch_history) => Ok(watch_history),
        Result12::Err(err) => {
            return Err(anyhow::anyhow!(err));
        }
    }
}

pub async fn get_success_history(
    individual_user_canister: &IndividualUserTemplate<'_>,
) -> Result<Vec<SuccessHistoryItemV1>> {
    match individual_user_canister.get_success_history().await? {
        Result10::Ok(success_history) => Ok(success_history),
        Result10::Err(err) => {
            return Err(anyhow::anyhow!(err));
        }
    }
}
