#
#  Copyright ©2024. Levo.ai Inc. All Rights Reserved.
#  You may not copy, reproduce, distribute, publish, display, perform, modify, create derivative works, transmit,
#  or in any way exploit any such software/code, nor may you distribute any part of this software/code over any network,
#  including a local area network, sell or offer it for commercial purposes.
#
import base64
import json
from typing import Optional, Tuple, Union

import requests

from .models import Response

# These are the keys that we'll be looking for inside the body to get the error code.
ERROR_CODE_KEYS = [
    "code",
    "status",
    "statusCode",
    "errorCode",
    "error_code",
    "status_code",
    "error",
]

STRING_CODE_TO_STATUS_DICT = {
    "unknown": 400,
    "invalid_input": 400,
    "param_should_be_present": 400,
    "failed": 400,
    "no_exchange_enabled": 400,
    "missing_input": 400,
    "offer_expired": 400,
    "user_blocked": 400,
    "unauthorized": 401,
    "user_does_not_exist": 404,
    "retry": 503,
    "wrong_params": 400,
    "token_auth_fail": 401,
    "invalid_token": 401,
    "forbidden": 403,
}


# pylint: disable=too-many-branches
def get_error_code_from_response_body(
    response: Union[str, bytes, Response, requests.Response]
) -> Optional[int]:
    """Check if the response body contains an error code and return it.

    Integer error codes take precedence over string error codes.
    """
    body_str = (
        response
        if isinstance(response, (str, bytes))
        else response.content
        if isinstance(response, requests.Response)
        else response.body
    ) or ""
    # TODO: Be consistent about base64 encoding of response body.
    try:
        body = json.loads(body_str)
    except Exception:
        try:
            decoded_body = base64.b64decode(body_str)
            encoding = "utf8"
            if not isinstance(response, (str, bytes)) and response.encoding:
                encoding = response.encoding
            response_body = decoded_body.decode(encoding, errors="replace")
            body = json.loads(response_body)
        except Exception:
            return None

    if not isinstance(body, dict):
        return None

    found_string_error_code = None

    for key in ERROR_CODE_KEYS:
        if value := body.get(key):
            if isinstance(value, int) or (isinstance(value, str) and value.isdigit()):
                status_code = int(value)
                if 100 <= status_code < 600:
                    return status_code
            elif (
                not found_string_error_code
                and isinstance(value, str)
                and value.casefold() in STRING_CODE_TO_STATUS_DICT
            ):
                found_string_error_code = STRING_CODE_TO_STATUS_DICT[value.casefold()]

    error_dict = {}
    # TODO: we should configure error dict's jsonpath per customer
    if (
        "error" in body
        and body["error"] is not None
        and isinstance(body["error"], dict)
    ):
        error_dict = body["error"]
    elif body.get("data") and isinstance(body["data"], dict):
        error_dict = body["data"]

    if error_dict:
        for key in ERROR_CODE_KEYS:
            if value := error_dict.get(key):
                if isinstance(value, int) or (
                    isinstance(value, str) and value.isdigit()
                ):
                    status_code = int(value)
                    if 100 <= status_code < 600:
                        return status_code
                elif (
                    not found_string_error_code
                    and isinstance(value, str)
                    and value.casefold() in STRING_CODE_TO_STATUS_DICT
                ):
                    found_string_error_code = STRING_CODE_TO_STATUS_DICT[
                        value.casefold()
                    ]
                    return found_string_error_code

    return found_string_error_code


def is_valid_2xx_response(
    response: Union[Response, requests.Response], return_code: bool = False
) -> Union[bool, Tuple[bool, int]]:
    """Check if the response is a valid 2xx response.

    In addition to checking the status code, we also check if the response body doesn't have any error codes because
    some APIs return 200 OK for error responses but the response body contains an error code.
    """
    if not response:
        return False if not return_code else (False, 0)

    if isinstance(response, requests.Response):
        response = Response.from_requests(response)

    # Check if the response is an error response.
    if response.status_code < 200 or response.status_code >= 300:
        return False if not return_code else (False, response.status_code)

    if response.body is not None:
        try:
            code = get_error_code_from_response_body(response)

            # If the code is present in the body, we have to return based on that.
            if code:
                return (
                    200 <= code < 300 if not return_code else (200 <= code < 300, code)
                )

        except Exception:
            pass
    return True if not return_code else (True, response.status_code)


def is_4xx_error_response(
    response: Union[Response, requests.Response], return_code: bool = False
) -> Union[bool, Tuple[bool, int]]:
    if isinstance(response, requests.Response):
        response = Response.from_requests(response)

    # Check if the response is an error response.
    if 400 <= response.status_code < 500:
        return True if not return_code else (True, response.status_code)

    if 200 <= response.status_code < 300 and response.body is not None:
        # Some APIs return 200 OK for error responses but the response body contains an error code.
        # So, we check if the response body contains an error code.
        try:
            code = get_error_code_from_response_body(response)

            # If the code is defined in the body, return based on that.
            if code:
                return (
                    400 <= code < 500 if not return_code else (400 <= code < 500, code)
                )
        except Exception:
            pass
    return False if not return_code else (False, response.status_code)
