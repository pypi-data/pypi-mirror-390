"""
API tests for Swagger documentation endpoint.

This module tests the health and accessibility of the Swagger/OpenAPI documentation endpoint.
"""

import os

import pytest
import requests
from hamcrest import assert_that, equal_to, is_in, less_than

from codemie_test_harness.tests import VERIFY_SSL

# Module-level constants
CODEMIE_API_DOMAIN = os.getenv("CODEMIE_API_DOMAIN")
SWAGGER_URL = f"{CODEMIE_API_DOMAIN}/docs"
OPENAPI_JSON_URL = f"{CODEMIE_API_DOMAIN}/openapi.json"


@pytest.mark.api
@pytest.mark.smoke
@pytest.mark.swagger
def test_swagger_endpoint_is_accessible():
    """
    Test that the Swagger documentation endpoint is accessible and returns a successful response.

    The test verifies:
    1. The endpoint responds with HTTP 200 status code
    2. The endpoint is reachable and healthy
    """
    response = requests.get(SWAGGER_URL, verify=VERIFY_SSL)

    assert_that(response.status_code, equal_to(200))


@pytest.mark.api
@pytest.mark.smoke
@pytest.mark.swagger
def test_swagger_endpoint_returns_html():
    """
    Test that the Swagger documentation endpoint returns HTML content.

    The test verifies:
    1. The response content type is HTML
    2. The response contains expected Swagger/OpenAPI keywords
    """

    response = requests.get(SWAGGER_URL, verify=VERIFY_SSL)

    assert_that(response.status_code, equal_to(200))

    content_type = response.headers.get("Content-Type", "")
    assert_that("text/html", is_in(content_type))

    # Verify the response contains Swagger/OpenAPI related content
    content = response.text.lower()
    keywords = ["swagger", "openapi", "api", "docs"]
    assert_that(any(keyword in content for keyword in keywords), equal_to(True))


@pytest.mark.api
@pytest.mark.smoke
@pytest.mark.swagger
def test_swagger_endpoint_response_time():
    """
    Test that the Swagger documentation endpoint responds within acceptable time.

    The test verifies:
    1. The endpoint responds within 5 seconds
    """
    timeout = 5  # seconds

    try:
        response = requests.get(SWAGGER_URL, verify=VERIFY_SSL, timeout=timeout)
        assert_that(response.status_code, equal_to(200))
        assert_that(response.elapsed.total_seconds(), less_than(timeout))
    except requests.exceptions.Timeout:
        pytest.fail(f"Swagger endpoint did not respond within {timeout} seconds")


@pytest.mark.api
@pytest.mark.smoke
@pytest.mark.swagger
def test_openapi_json_endpoint(client):
    """
    Test that the OpenAPI JSON endpoint returns valid JSON with expected metadata.

    The test verifies:
    1. The endpoint responds with HTTP 200 status code
    2. The response is valid JSON
    3. The info.title field equals "Codemie"
    4. The info.description field equals "Smart AI assistant 'CodeMie'"
    """
    headers = {"Authorization": f"Bearer {client.token}"}
    response = requests.get(OPENAPI_JSON_URL, headers=headers, verify=VERIFY_SSL)

    assert_that(response.status_code, equal_to(200))

    # Verify response is valid JSON
    openapi_spec = response.json()

    # Verify info.title
    assert_that(openapi_spec.get("info", {}).get("title"), equal_to("Codemie"))

    # Verify info.description
    assert_that(
        openapi_spec.get("info", {}).get("description"),
        equal_to("Smart AI assistant 'CodeMie'"),
    )
