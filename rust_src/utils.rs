use chrono::{DateTime, Utc};

use crate::canister::individual_user_template::SystemTime;

pub fn to_rfc3339_did_systemtime(dt: &SystemTime) -> String {
    let sys_time = to_system_time(dt.nanos_since_epoch, dt.secs_since_epoch);
    to_rfc3339(sys_time)
}

pub fn to_rfc3339(dt: std::time::SystemTime) -> String {
    let dt: DateTime<Utc> = dt.into();
    dt.to_rfc3339()
}

pub fn to_system_time(nanos_since_epoch: u32, secs_since_epoch: u64) -> std::time::SystemTime {
    let duration = std::time::Duration::new(secs_since_epoch, nanos_since_epoch);
    std::time::SystemTime::UNIX_EPOCH + duration
}
