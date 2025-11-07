#
#  Copyright ©2024. Levo.ai Inc. All Rights Reserved.
#  You may not copy, reproduce, distribute, publish, display, perform, modify, create derivative works, transmit,
#  or in any way exploit any such software/code, nor may you distribute any part of this software/code over any network,
#  including a local area network, sell or offer it for commercial purposes.
#
import base64

import pytest
import requests

from levo_commons.models import Response
from levo_commons.request_utils import (
    get_error_code_from_response_body,
    is_4xx_error_response,
    is_valid_2xx_response,
)


def test_is_4xx_error_response():
    response = Response(
        status_code=400,
        body="{}",
        headers={},
        method="GET",
        uri="/test",
        message="Bad Request",
        http_version="HTTP/1.1",
        encoding=None,
    )
    response.status_code = 400
    assert is_4xx_error_response(response) is True

    # Add json body to the response and verify
    response.body = '{"error": "Bad Request"}'
    assert is_4xx_error_response(response) is True

    # Set status code to 200 but indicate error in the body
    response.status_code = 200
    response.body = '{"error": {"code": 400, "message": "Bad Request"}}'
    assert is_4xx_error_response(response) is True

    response.body = '{"status_code": 400, "message": "Bad Request"}'
    assert is_4xx_error_response(response) is True

    response.status_code = 500
    assert is_4xx_error_response(response) is False


def test_is_valid_2xx_response():
    response = Response(
        status_code=200,
        body="{}",
        headers={},
        method="GET",
        uri="/test",
        message="OK",
        http_version="HTTP/1.1",
        encoding=None,
    )
    assert is_valid_2xx_response(response) is True

    response.status_code = 201
    assert is_valid_2xx_response(response) is True

    response.status_code = 204
    assert is_valid_2xx_response(response) is True

    response.status_code = 400
    assert is_valid_2xx_response(response) is False

    response.status_code = 500
    assert is_valid_2xx_response(response) is False

    response.status_code = 200
    response.body = '{"errorCode": 400, "errorMessage": "Bad Request"}'
    assert is_valid_2xx_response(response) is False

    response.body = '{"statusCode": 400, "errorMessage": "Bad Request"}'
    assert is_valid_2xx_response(response) is False

    response.body = '{"error": {"statusCode": 400, "errorMessage": "Bad Request"}}'
    assert is_valid_2xx_response(response) is False

    response.body = base64.b64encode(
        '{"error": {"statusCode": 400, "errorMessage": "Bad Request"}}'.encode()
    )
    assert is_valid_2xx_response(response) is False


def test_string_error_code():
    response = requests.Response()
    response._content = '{"success":false,"code":"unauthorized","data":null,"msg":"Authorization failed"}'
    assert get_error_code_from_response_body(response) == 401

    response._content = '{"success":false,"code":"invalid_input","data":null,"msg":"Invalid auth token provided"}'
    assert get_error_code_from_response_body(response) == 400

    response._content = (
        '{"success":false,"code":"RETRY","data":{"msg":"Please try again."},"msg":""}'
    )
    assert get_error_code_from_response_body(response) == 503

    response._content = (
        '{"success":true,"code":"OK","data":{"IS_FUTURE_ENABLED":false},"msg":""}'
    )
    assert get_error_code_from_response_body(response) is None

    response._content = '{"success":true,"code":"200","data":{"express_kyc_status":"NOT_STARTED"},"msg":""}'
    assert get_error_code_from_response_body(response) == 200

    response._content = (
        '{"success":false,"status":"retry","error":{"code":401},"data":{'
        '"express_kyc_status":"NOT_STARTED"},"msg":""}'
    )
    assert get_error_code_from_response_body(response) == 401

    response._content = '{"success":true,"code":"401","data":{"express_kyc_status":"NOT_STARTED"},"msg":""}'
    assert get_error_code_from_response_body(response) == 401

    response._content = '{"result":41406, "data":{"error":"wrong_params"},"msg":""}'
    assert get_error_code_from_response_body(response) == 400

    response._content = (
        '{"result":41406, "code":"403", "data":{"error":"invalid_token"},"msg":""}'
    )
    assert get_error_code_from_response_body(response) == 403

    response._content = '{"result":41406, "data":{"error":"invalid_token"},"msg":""}'
    assert get_error_code_from_response_body(response) == 401


@pytest.mark.parametrize("res_body", ["[]", "12345"])
def test_non_dict_json_body(res_body):
    response = requests.Response()
    response._content = res_body
    try:
        assert get_error_code_from_response_body(response) is None
    except AttributeError:
        pytest.fail("Should not raise AttributeError")
