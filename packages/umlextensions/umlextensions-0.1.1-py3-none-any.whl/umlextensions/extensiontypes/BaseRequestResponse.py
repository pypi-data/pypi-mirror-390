
from dataclasses import dataclass


@dataclass
class BaseRequestResponse:
    cancelled:     bool      = False
