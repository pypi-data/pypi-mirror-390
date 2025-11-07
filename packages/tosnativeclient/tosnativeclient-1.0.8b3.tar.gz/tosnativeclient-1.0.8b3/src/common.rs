use crate::tos_error::map_error;
use bytes::Bytes;
use pprof::ProfilerGuard;
use pyo3::types::PyBytes;
use pyo3::{pyfunction, Bound, PyResult, Python};
use std::fs::File;
use std::sync::Arc;
use std::thread;
use std::thread::sleep;
use std::time::Duration;
use tracing::warn;

#[pyfunction]
pub fn async_write_profile(py: Python<'_>, seconds: i64, mut file_path: String) -> PyResult<()> {
    if seconds <= 0 {
        return Ok(());
    }

    if file_path.is_empty() {
        file_path = String::from("cpu_profile.html");
    } else if !file_path.ends_with(".html") {
        file_path += ".html";
    }
    py.allow_threads(|| match ProfilerGuard::new(100) {
        Err(ex) => Err(map_error(ex)),
        Ok(guard) => {
            thread::spawn(move || {
                sleep(Duration::from_secs(seconds as u64));
                if let Ok(fd) = File::create(file_path) {
                    if let Ok(report) = guard.report().build() {
                        let mut options = pprof::flamegraph::Options::default();
                        options.image_width = Some(2500);
                        if let Err(ex) = report.flamegraph_with_options(fd, &mut options) {
                            warn!("flamegraph error, {:?}", ex);
                        }
                    }
                }
            });
            Ok(())
        }
    })
}
