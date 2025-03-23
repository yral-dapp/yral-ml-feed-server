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
