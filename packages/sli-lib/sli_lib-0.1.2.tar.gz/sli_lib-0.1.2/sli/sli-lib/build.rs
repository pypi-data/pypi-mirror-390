use std::fs;
use std::io::Write;
use std::path::PathBuf;
use std::println;
use std::{env, process::Command};

fn main() {
    println!("cargo::rerun-if-changed=tests/test_files");
    println!("cargo::rerun-if-changed=tests/unsat_test_files");
    let out_dir = std::env::var("OUT_DIR").unwrap();
    let version = get_version_and_commit();
    let mut sli_version_file =
        fs::File::create(PathBuf::from(out_dir).join("sli_version.rs")).unwrap();
    write!(&mut sli_version_file, "pub static VERSION: &str = \"",).unwrap();
    match version {
        Some(Version {
            tag: Some(tag),
            commit,
        }) => {
            write!(&mut sli_version_file, "{}-{}", tag, commit).unwrap();
        }
        Some(Version { tag: None, commit }) => {
            write!(
                &mut sli_version_file,
                "{}-{}",
                env!("CARGO_PKG_VERSION"),
                commit
            )
            .unwrap();
        }
        None => {
            write!(&mut sli_version_file, "{}", env!("CARGO_PKG_VERSION"),).unwrap();
        }
    }
    writeln!(&mut sli_version_file, "\";",).unwrap();
}

struct Version {
    tag: Option<String>,
    commit: String,
}

fn get_version_and_commit() -> Option<Version> {
    println!("cargo:rerun-if-changed=../../.git/HEAD");
    let tag = Command::new("git")
        .args(["describe", "--tags", "match=\"sli-lib/*\"", "--abbrev=0"])
        .output()
        .ok()?;
    let tag = if tag.status.success() {
        Some(String::from_utf8(tag.stdout).unwrap().trim().to_string())
    } else {
        None
    };
    let commit = Command::new("git")
        .args(["rev-parse", "HEAD"])
        .output()
        .ok()?;
    let commit = if !commit.status.success() {
        return None;
    } else {
        let commit = String::from_utf8(commit.stdout).unwrap().trim().to_string();
        commit
    };
    Version { tag, commit }.into()
}
