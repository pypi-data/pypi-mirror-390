"""
Test utilities for automation_lib integration tests.
"""
import os

import pytest


def skip_unless_integration_test(obj):
    """
    Decorator to skip a test or test class unless INTEGRATION_TEST environment variable is set.
    
    Usage:
        @skip_unless_integration_test
        class TestMyIntegration:
            ...
            
        @skip_unless_integration_test
        def test_something_integration():
            ...
    """
    return pytest.mark.skipif(
        not os.getenv("INTEGRATION_TEST"),
        reason="Integration tests are disabled. Set INTEGRATION_TEST=1 to enable."
    )(obj)


def check_openai_api_key_set() -> bool:
    """
    Check if OpenAI API key is set in environment variables.
    
    Returns:
        bool: True if OPENAI_API_KEY is set and not empty, False otherwise.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    return api_key is not None and api_key.strip() != ""


def check_google_cloud_credentials_path_set() -> bool:
    """
    Check if Google Cloud credentials path is set in environment variables.
    
    Returns:
        bool: True if GOOGLE_APPLICATION_CREDENTIALS is set and not empty, False otherwise.
    """
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    return credentials_path is not None and credentials_path.strip() != ""


def check_gemini_api_key_set() -> bool:
    """
    Check if Gemini API key is set in environment variables.
    
    Returns:
        bool: True if GEMINI_API_KEY is set and not empty, False otherwise.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    return api_key is not None and api_key.strip() != ""
