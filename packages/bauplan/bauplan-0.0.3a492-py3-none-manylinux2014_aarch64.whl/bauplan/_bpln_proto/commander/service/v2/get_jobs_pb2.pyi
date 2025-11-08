from bauplan._bpln_proto.commander.service.v2 import common_pb2 as _common_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import (
    ClassVar as _ClassVar,
    Iterable as _Iterable,
    Mapping as _Mapping,
    Optional as _Optional,
    Union as _Union,
)

DESCRIPTOR: _descriptor.FileDescriptor

class GetJobsRequest(_message.Message):
    __slots__ = (
        'job_ids',
        'all_users',
        'filter_users',
        'filter_kind',
        'filter_status',
        'filter_started_after',
        'filter_started_before',
        'filter_finished_after',
        'filter_finished_before',
    )
    JOB_IDS_FIELD_NUMBER: _ClassVar[int]
    ALL_USERS_FIELD_NUMBER: _ClassVar[int]
    FILTER_USERS_FIELD_NUMBER: _ClassVar[int]
    FILTER_KIND_FIELD_NUMBER: _ClassVar[int]
    FILTER_STATUS_FIELD_NUMBER: _ClassVar[int]
    FILTER_STARTED_AFTER_FIELD_NUMBER: _ClassVar[int]
    FILTER_STARTED_BEFORE_FIELD_NUMBER: _ClassVar[int]
    FILTER_FINISHED_AFTER_FIELD_NUMBER: _ClassVar[int]
    FILTER_FINISHED_BEFORE_FIELD_NUMBER: _ClassVar[int]
    job_ids: _containers.RepeatedScalarFieldContainer[str]
    all_users: bool
    filter_users: _containers.RepeatedScalarFieldContainer[str]
    filter_kind: _common_pb2.JobKind
    filter_status: _common_pb2.JobStateType
    filter_started_after: _timestamp_pb2.Timestamp
    filter_started_before: _timestamp_pb2.Timestamp
    filter_finished_after: _timestamp_pb2.Timestamp
    filter_finished_before: _timestamp_pb2.Timestamp
    def __init__(
        self,
        job_ids: _Optional[_Iterable[str]] = ...,
        all_users: bool = ...,
        filter_users: _Optional[_Iterable[str]] = ...,
        filter_kind: _Optional[_Union[_common_pb2.JobKind, str]] = ...,
        filter_status: _Optional[_Union[_common_pb2.JobStateType, str]] = ...,
        filter_started_after: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        filter_started_before: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        filter_finished_after: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        filter_finished_before: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
    ) -> None: ...

class GetJobsResponse(_message.Message):
    __slots__ = ('jobs',)
    JOBS_FIELD_NUMBER: _ClassVar[int]
    jobs: _containers.RepeatedCompositeFieldContainer[_common_pb2.JobInfo]
    def __init__(self, jobs: _Optional[_Iterable[_Union[_common_pb2.JobInfo, _Mapping]]] = ...) -> None: ...
