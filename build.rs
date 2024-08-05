use std::{env, path::PathBuf};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let proto_file = "contracts/projects/ml_feed/ml_feed.proto";
    let out_dir = PathBuf::from(env::var("OUT_DIR").unwrap());

    tonic_build::configure()
        .build_client(false)
        .build_server(true)
        .file_descriptor_set_path(out_dir.join("ml_feed_descriptor.bin"))
        .out_dir(out_dir)
        .compile(&[proto_file], &["proto"])?;

    Ok(())
}
