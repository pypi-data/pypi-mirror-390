use crate::tos_error::map_error;
use pprof::ProfilerGuard;
use pyo3::{pyclass, pyfunction, PyResult, Python};
use std::fs::File;
use std::thread;
use std::thread::sleep;
use std::time::Duration;
use tracing::warn;
use tracing_appender::non_blocking::WorkerGuard;

#[pyfunction]
#[pyo3(signature = (seconds, file_path, image_width=1200))]
pub fn async_write_profile(
    py: Python<'_>,
    seconds: i64,
    mut file_path: String,
    mut image_width: usize,
) -> PyResult<()> {
    if seconds <= 0 {
        return Ok(());
    }

    if file_path.is_empty() {
        file_path = String::from("cpu_profile.html");
    } else if !file_path.ends_with(".html") {
        file_path += ".html";
    }
    if image_width <= 0 {
        image_width = 1200;
    }
    py.allow_threads(|| match ProfilerGuard::new(100) {
        Err(ex) => Err(map_error(ex)),
        Ok(guard) => {
            thread::spawn(move || {
                sleep(Duration::from_secs(seconds as u64));
                if let Ok(fd) = File::create(file_path) {
                    if let Ok(report) = guard.report().build() {
                        let mut options = pprof::flamegraph::Options::default();
                        options.image_width = Some(image_width);
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
#[pyclass(name = "TosLogGuard", module = "tosnativeclient")]
pub struct TosLogGuard {
    _guard: WorkerGuard,
}

#[pyfunction]
#[pyo3(signature = (directives, directory, file_name_prefix))]
pub fn init_tracing_log(
    directives: String,
    directory: String,
    file_name_prefix: String,
) -> PyResult<Option<TosLogGuard>> {
    if directory == "" {
        return Ok(None);
    }
    let guard: WorkerGuard = ve_tos_rust_sdk::common::init_tracing_log(
        directives.clone(),
        directory.clone(),
        file_name_prefix.clone(),
    );
    Ok(Some(TosLogGuard { _guard: guard }))
}
