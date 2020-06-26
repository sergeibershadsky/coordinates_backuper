from dataclasses import dataclass


@dataclass
class UploadInfo:
    href: str
    method: str
    templated: bool
    operation_id: str
