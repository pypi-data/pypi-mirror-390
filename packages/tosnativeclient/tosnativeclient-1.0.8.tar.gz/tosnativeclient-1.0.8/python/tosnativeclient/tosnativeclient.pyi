from typing import List, Dict, Any

from typing import Optional


def async_write_profile(seconds: int, file_path: str, image_width: int = 1200) -> None:
    ...


def init_tracing_log(directives: str = '', directory: str = '',
                     file_name_prefix: str = '') -> Any:
    ...


class TosError(object):
    message: str
    status_code: Optional[int]
    ec: str
    request_id: str


class TosException(Exception):
    args: List[TosError]


class TosObject(object):
    bucket: str
    key: str
    size: int
    etag: str


class ListObjectsResult(object):
    contents: List[TosObject]
    common_prefixes: List[str]


class ListStream(object):
    bucket: str
    prefix: str
    delimiter: str
    max_keys: int
    continuation_token: str
    start_after: str
    list_background_buffer_count: int

    def __iter__(self) -> ListStream: ...

    def __next__(self) -> ListObjectsResult: ...

    def close(self) -> None: ...

    def current_prefix(self) -> Optional[str]: ...

    def current_continuation_token(self) -> Optional[str]: ...


class ReadStream(object):
    bucket: str
    key: str
    size: int
    etag: str

    def read(self, offset: int, length: int) -> Optional[bytes]:
        ...

    def close(self) -> None:
        ...


class WriteStream(object):
    bucket: str
    key: str
    storage_class: Optional[str]

    def write(self, data: bytes) -> int:
        ...

    def close(self) -> None:
        ...


class TosClient(object):
    region: str
    endpoint: str
    ak: str
    sk: str
    part_size: int
    max_retry_count: int
    max_prefetch_tasks: int
    shared_prefetch_tasks: int
    enable_crc: bool

    def __init__(self, region: str, endpoint: str, ak: str = '', sk: str = '', part_size: int = 8388608,
                 max_retry_count: int = 3, max_prefetch_tasks: int = 3, shared_prefetch_tasks: int = 20,
                 enable_crc: bool = True):
        ...

    def list_objects(self, bucket: str, prefix: str = '', max_keys: int = 1000, delimiter: str = '',
                     continuation_token: str = '', start_after: str = '',
                     list_background_buffer_count: int = 1) -> ListStream:
        ...

    def head_object(self, bucket: str, key: str) -> TosObject:
        ...

    def get_object(self, bucket: str, key: str, etag: str, size: int) -> ReadStream:
        ...

    def put_object(self, bucket: str, key: str, storage_class: Optional[str] = '') -> WriteStream:
        ...


class HeadObjectInput(object):
    bucket: str
    key: str
    version_id: str

    def __init__(self, bucket: str, key: str, version_id: str = ''):
        ...


class HeadObjectOutput(object):
    request_id: str
    status_code: int
    header: Dict[str, str]
    content_length: int
    etag: str
    version_id: str
    hash_crc64ecma: int


class DeleteObjectInput(object):
    bucket: str
    key: str
    version_id: str

    def __init__(self, bucket: str, key: str, version_id: str = ''):
        ...


class DeleteObjectOutput(object):
    request_id: str
    status_code: int
    header: Dict[str, str]
    delete_marker: bool
    version_id: str


class GetObjectInput(object):
    bucket: str
    key: str
    version_id: str
    range: str

    def __init__(self, bucket: str, key: str, version_id: str = '', range: str = ''):
        ...


class GetObjectOutput(object):
    request_id: str
    status_code: int
    header: Dict[str, str]
    content_length: int
    etag: str
    version_id: str
    content_range: str
    hash_crc64ecma: int

    def read_all(self) -> Optional[bytes]:
        ...

    def read(self) -> Optional[bytes]:
        ...


class PutObjectFromBufferInput(object):
    bucket: str
    key: str
    content: bytes

    def __init__(self, bucket: str, key: str, content: bytes):
        ...


class PutObjectFromFileInput(object):
    bucket: str
    key: str
    file_path: str

    def __init__(self, bucket: str, key: str, file_path: str):
        ...


class PutObjectOutput(object):
    request_id: str
    status_code: int
    header: Dict[str, str]
    etag: str
    version_id: str
    hash_crc64ecma: int


class TosRawClient(object):
    region: str
    endpoint: str
    ak: str
    sk: str
    connection_timeout: int
    request_timeout: int
    max_connections: int
    max_retry_count: int

    def __init__(self, region: str, endpoint: str, ak: str = '', sk: str = '', connection_timeout: int = 10000,
                 request_timeout: int = 120000, max_connections: int = 1024, max_retry_count: int = 3):
        ...

    def head_object(self, input: HeadObjectInput) -> HeadObjectOutput:
        ...

    def delete_object(self, input: DeleteObjectInput) -> DeleteObjectOutput:
        ...

    def get_object(self, input: GetObjectInput) -> GetObjectOutput:
        ...

    def put_object_from_buffer(self, input: PutObjectFromBufferInput) -> PutObjectOutput:
        ...

    def put_object_from_file(self, input: PutObjectFromFileInput) -> PutObjectOutput:
        ...
