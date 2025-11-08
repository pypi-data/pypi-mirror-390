use crate::tos_client::InnerTosClient;
use crate::tos_error::{map_error_from_string, map_tos_error};
use crate::tos_model::ListObjectsResult;
use arc_swap::ArcSwap;
use async_channel::Receiver;
use pyo3::{pyclass, pymethods, PyRef, PyRefMut, PyResult, Python};
use std::sync::atomic::{AtomicI8, Ordering};
use std::sync::{Arc, RwLock};
use tokio::runtime::Runtime;
use tokio::task::JoinHandle;
use ve_tos_rust_sdk::asynchronous::object::ObjectAPI;
use ve_tos_rust_sdk::error::TosError;
use ve_tos_rust_sdk::object::{ListObjectsType2Input, ListObjectsType2Output};

const DEFAULT_BUFFER_COUNT: usize = 3;
#[pyclass(name = "ListStream", module = "tosnativeclient")]
pub struct ListStream {
    client: Arc<InnerTosClient>,
    runtime: Arc<Runtime>,
    paginator: RwLock<Option<Paginator>>,
    closed: AtomicI8,
    #[pyo3(get)]
    bucket: String,
    #[pyo3(get)]
    prefix: String,
    #[pyo3(get)]
    delimiter: String,
    #[pyo3(get)]
    max_keys: isize,
    #[pyo3(get)]
    continuation_token: String,
    #[pyo3(get)]
    start_after: String,
    #[pyo3(get)]
    list_background_buffer_count: isize,
}

#[pymethods]
impl ListStream {
    pub fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    pub fn __next__(slf: PyRefMut<'_, Self>) -> PyResult<Option<ListObjectsResult>> {
        {
            let pg = slf.paginator.read().unwrap();
            if pg.is_some() {
                return slf.next_page(pg.as_ref(), slf.py());
            }
        }

        if slf.closed.load(Ordering::Acquire) == 1 {
            return Err(map_error_from_string("ListStream is closed"));
        }

        let mut pg = slf.paginator.write().unwrap();
        if pg.is_none() {
            *pg = slf.list_background(slf.py());
        }
        slf.next_page(pg.as_ref(), slf.py())
    }

    pub fn close(slf: PyRef<'_, Self>) {
        if let Ok(_) = slf
            .closed
            .compare_exchange(0, 1, Ordering::AcqRel, Ordering::Relaxed)
        {
            if let Some(pg) = slf.paginator.write().unwrap().as_mut() {
                pg.receiver.close();
                let runtime = slf.runtime.clone();
                slf.py().allow_threads(|| {
                    runtime.block_on(async {
                        pg.close().await;
                    })
                });
            }
        }
    }

    pub fn current_prefix(&self) -> PyResult<Option<String>> {
        let pg = self.paginator.read().unwrap();
        match pg.as_ref() {
            None => Ok(None),
            Some(pg) => Ok(Some(pg.current_prefix())),
        }
    }

    pub fn current_continuation_token(&self) -> PyResult<Option<String>> {
        let pg = self.paginator.read().unwrap();
        match pg.as_ref() {
            None => Ok(None),
            Some(pg) => Ok(Some(pg.current_continuation_token())),
        }
    }
}

impl ListStream {
    pub(crate) fn new(
        client: Arc<InnerTosClient>,
        runtime: Arc<Runtime>,
        bucket: String,
        prefix: String,
        delimiter: String,
        max_keys: isize,
        continuation_token: String,
        start_after: String,
        list_background_buffer_count: isize,
    ) -> Self {
        Self {
            client,
            runtime,
            paginator: RwLock::new(None),
            closed: AtomicI8::new(0),
            bucket,
            prefix,
            delimiter,
            max_keys,
            continuation_token,
            start_after,
            list_background_buffer_count,
        }
    }

    pub(crate) fn list_background(&self, py: Python) -> Option<Paginator> {
        let mut buffer_count = self.list_background_buffer_count as usize;
        if buffer_count <= 0 {
            buffer_count = DEFAULT_BUFFER_COUNT;
        }
        let (sender, receiver) = async_channel::bounded(buffer_count);
        let client = self.client.clone();
        let mut input = ListObjectsType2Input::new(self.bucket.as_str());
        input.set_prefix(self.prefix.as_str());
        input.set_max_keys(self.max_keys);
        input.set_delimiter(self.delimiter.as_str());
        if self.continuation_token != "" {
            input.set_continuation_token(self.continuation_token.as_str());
        }
        if self.start_after != "" {
            input.set_start_after(self.start_after.as_str());
        }
        let wait_list_background = py.allow_threads(|| {
            self.runtime.spawn(async move {
                let mut need_break = false;
                if input.delimiter() == "" {
                    loop {
                        let result = client.list_objects_type2(&input).await;
                        if let Ok(ref o) = result {
                            if o.is_truncated() {
                                input.set_continuation_token(o.next_continuation_token());
                            } else {
                                need_break = true;
                            }
                        } else {
                            need_break = true;
                        }
                        if let Err(_) = sender.send((need_break, result)).await {
                            need_break = true
                        }
                        if need_break {
                            break;
                        }
                    }
                } else {
                    let mut prefixes = Vec::with_capacity(16);
                    let mut last_page_end = false;
                    loop {
                        if last_page_end {
                            let prefix = prefixes.remove(0);
                            input.set_prefix(prefix);
                            input.set_start_after("");
                            input.set_continuation_token("");
                            last_page_end = false;
                        }
                        let result = client.list_objects_type2(&input).await;
                        if let Ok(ref o) = result {
                            if o.is_truncated() {
                                input.set_continuation_token(o.next_continuation_token());
                            } else {
                                last_page_end = true;
                            }

                            for cp in o.common_prefixes() {
                                prefixes.push(cp.prefix().to_string());
                            }
                            need_break = last_page_end && prefixes.is_empty();
                        } else {
                            need_break = true;
                        }

                        if let Err(_) = sender.send((need_break, result)).await {
                            need_break = true;
                        }
                        if need_break {
                            break;
                        }
                    }
                }
            })
        });
        Some(Paginator {
            is_end: ArcSwap::new(Arc::new(false)),
            last_err: ArcSwap::new(Arc::new(None)),
            current_prefix: ArcSwap::new(Arc::new(self.prefix.clone())),
            current_continuation_token: ArcSwap::new(Arc::new(self.continuation_token.clone())),
            receiver,
            wait_list_background: Some(wait_list_background),
        })
    }

    pub(crate) fn next_page(
        &self,
        paginator: Option<&Paginator>,
        py: Python,
    ) -> PyResult<Option<ListObjectsResult>> {
        match paginator {
            None => Ok(None),
            Some(pg) => {
                match pg.has_next() {
                    Err(ex) => return Err(map_tos_error(ex)),
                    Ok(has_next) => {
                        if !has_next {
                            return Ok(None);
                        }
                    }
                }

                py.allow_threads(|| {
                    self.runtime.block_on(async {
                        match pg.next_page().await {
                            Ok(output) => Ok(Some(ListObjectsResult::new(output))),
                            Err(ex) => Err(map_tos_error(ex)),
                        }
                    })
                })
            }
        }
    }
}

pub(crate) struct Paginator {
    is_end: ArcSwap<bool>,
    last_err: ArcSwap<Option<TosError>>,
    current_prefix: ArcSwap<String>,
    current_continuation_token: ArcSwap<String>,
    receiver: Receiver<(bool, Result<ListObjectsType2Output, TosError>)>,
    wait_list_background: Option<JoinHandle<()>>,
}

impl Paginator {
    fn has_next(&self) -> Result<bool, TosError> {
        if let Some(err) = self.last_err.load().as_ref() {
            return Err(err.clone());
        }
        Ok(!*self.is_end.load().as_ref())
    }

    fn current_prefix(&self) -> String {
        self.current_prefix.load().to_string()
    }
    fn current_continuation_token(&self) -> String {
        self.current_continuation_token.load().to_string()
    }

    async fn close(&mut self) {
        if let Some(wait_list_background) = self.wait_list_background.take() {
            let _ = wait_list_background.await;
        }
    }

    async fn next_page(&self) -> Result<ListObjectsType2Output, TosError> {
        if let Some(e) = self.last_err.load().as_ref() {
            return Err(e.clone());
        }
        if *self.is_end.load().as_ref() {
            return Err(TosError::TosClientError {
                message: "no next page error".to_string(),
                cause: None,
                request_url: "".to_string(),
            });
        }

        match self.receiver.recv().await {
            Err(_) => {
                self.is_end.store(Arc::new(true));
                Err(TosError::TosClientError {
                    message: "no next page error".to_string(),
                    cause: None,
                    request_url: "".to_string(),
                })
            }
            Ok((is_end, result)) => match result {
                Err(e) => {
                    self.last_err.store(Arc::new(Some(e.clone())));
                    Err(e)
                }
                Ok(output) => {
                    self.current_prefix
                        .store(Arc::new(output.prefix().to_string()));
                    self.current_continuation_token
                        .store(Arc::new(output.continuation_token().to_string()));
                    if is_end {
                        self.is_end.store(Arc::new(true));
                    }
                    Ok(output)
                }
            },
        }
    }
}
