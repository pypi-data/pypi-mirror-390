"""preferred response class for all API requests"""

__all__ = ["STREAM_FILE_PATH", "ResponseGetData", "find_ip", "RequestMetadata"]

import re
from dataclasses import dataclass, field
from typing import Any, Optional

import httpx
import requests
from bs4 import BeautifulSoup


@dataclass
class RequestMetadata:
    url: str
    headers: dict = field(repr=False, default_factory=dict)
    body: Optional[str] = field(default=None)
    params: Optional[dict] = field(default=None)

    def to_dict(self, auth_headers: Optional[list[str]] = None) -> dict:
        """returns dict representation of RequestMetadata"""

        return {
            "url": self.url,
            "headers": {
                k: v for k, v in self.headers.items() if k not in (auth_headers or [])
            },
            "body": self.body,
            "params": self.params,
        }


@dataclass
class ResponseGetData:
    """preferred response class for all API Requests"""

    status: int
    response: dict[str, Any] | str | list[Any]
    is_success: bool

    request_metadata: Optional[RequestMetadata] = field(default=None)
    additional_information: Optional[dict] = field(default=None, repr=False)

    def to_dict(self, is_exclude_response: bool = True) -> dict:
        """returns dict representation of ResponseGetData"""
        return {
            "status": self.status,
            "response": None if is_exclude_response else self.response,
            "is_success": self.is_success,
            "request_metadata": (
                self.request_metadata.to_dict() if self.request_metadata else None
            ),
            "additional_information": self.additional_information,
        }

    @classmethod
    def from_requests_response(
        cls,
        res: requests.Response,
        request_metadata: Optional[RequestMetadata] = None,
        additional_information: Optional[dict] = None,
    ) -> "ResponseGetData":
        """returns ResponseGetData from requests.Response"""

        # Check for JSON responses
        response = None
        if res.ok:
            if "application/json" in res.headers.get("Content-Type", ""):
                response = res.json()
            else:
                response = res.text

            return cls(
                status=res.status_code,
                response=response,
                additional_information=additional_information,
                request_metadata=request_metadata,
                is_success=True,
            )

        # Error responses
        return cls(
            status=res.status_code,
            response=res.reason,
            additional_information=additional_information,
            request_metadata=request_metadata,
            is_success=False,
        )

    @classmethod
    def from_httpx_response(
        cls,
        res: httpx.Response,
        request_metadata: Optional[RequestMetadata] = None,
        additional_information: Optional[dict] = None,
    ) -> "ResponseGetData":
        """returns ResponseGetData from httpx.Response"""

        # Check if response is successful
        ok = 200 <= res.status_code <= 399

        if ok:
            content_type = res.headers.get("Content-Type", "")

            # Try to parse as JSON if content type indicates it
            response = res.text  # Default to text
            if "application/json" in content_type:
                try:
                    response = res.json()
                except ValueError:
                    pass  # Keep as text if JSON parse fails

            return cls(
                status=res.status_code,
                response=response,
                is_success=True,
                additional_information=additional_information,
                request_metadata=request_metadata,
            )

        # Error responses
        response_text = (
            res.reason_phrase if hasattr(res, "reason_phrase") else "Unknown reason"
        )
        return cls(
            status=res.status_code,
            response=response_text,
            is_success=False,
            request_metadata=request_metadata,
            additional_information=additional_information,
        )

    @classmethod
    async def from_looper(
        cls,
        res: "ResponseGetData",
        array: list,
    ) -> "ResponseGetData":
        """async method returns ResponseGetData with array response"""

        if not res.is_success:
            return res

        res.response = array
        return res


def find_ip(html: str, html_tag: str = "p") -> Optional[str]:
    """Extract IP address from HTML content.

    Args:
        html: HTML content to search
        html_tag: HTML tag to search within (default: "p")

    Returns:
        IP address string if found, None otherwise
    """
    ip_address_regex = r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
    soup = BeautifulSoup(html, "html.parser")

    tag = soup.find(html_tag)
    if not tag:
        return None

    matches = re.findall(ip_address_regex, str(tag))
    return matches[0] if matches else None


STREAM_FILE_PATH = "__large-file.json"
