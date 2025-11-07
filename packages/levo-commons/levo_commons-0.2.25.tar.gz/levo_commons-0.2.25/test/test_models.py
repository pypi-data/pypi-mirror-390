#
#  Copyright ©2024. Levo.ai Inc. All Rights Reserved.
#  You may not copy, reproduce, distribute, publish, display, perform, modify, create derivative works, transmit,
#  or in any way exploit any such software/code, nor may you distribute any part of this software/code over any network,
#  including a local area network, sell or offer it for commercial purposes.
#

import pytest

from levo_commons.models import AfterTestExecutionPayload, TestResult
from levo_commons.status import Status


def test_after_test_execution_payload_with_status_code():
    """Test that status_code field can be set and retrieved."""
    payload = AfterTestExecutionPayload(
        test_case_id="test-123",
        name="Test Case",
        method="GET",
        path="/api/test",
        relative_path="/api/test",
        status=Status.success,
        elapsed_time=1.5,
        result=None,
        status_code=200,
    )
    assert payload.status_code == 200


def test_after_test_execution_payload_without_status_code():
    """Test that status_code field defaults to None."""
    payload = AfterTestExecutionPayload(
        test_case_id="test-123",
        name="Test Case",
        method="GET",
        path="/api/test",
        relative_path="/api/test",
        status=Status.success,
        elapsed_time=1.5,
        result=None,
    )
    assert payload.status_code is None
