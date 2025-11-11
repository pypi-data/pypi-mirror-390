use std::format;
use std::panic;
use std::println;
use std::str;

fn main() {
    println!("cargo:rerun-if-changed=build.rs");
    handle_store_impl();
}

const STORES: [&str; 2] = ["hash", "roaring"];
const DEFAULT: &str = "roaring";
const CFG_NAME: &str = "backend_store";
const ENV_VAR_NAME: &str = "SLI_BACKEND_STORE";

fn handle_store_impl() {
    let store_values = STORES
        .iter()
        .map(|f| format!("\"{:}\"", f))
        .collect::<Vec<_>>()
        .join(",");
    println!("cargo:rerun-if-env-changed={}", ENV_VAR_NAME);
    println!(
        "cargo:rustc-check-cfg=cfg({}, values({}))",
        CFG_NAME, store_values
    );
    if let Ok(val) = std::env::var(ENV_VAR_NAME) {
        if STORES.iter().find(|&f| *f == val).is_none() {
            panic!(
                "Invalid {} option, valid options are: {:?}",
                ENV_VAR_NAME, STORES
            );
        }
        println!("cargo:rustc-cfg={}=\"{}\"", CFG_NAME, val);
    } else {
        println!("cargo:rustc-cfg={}=\"{}\"", CFG_NAME, DEFAULT);
    }
}
