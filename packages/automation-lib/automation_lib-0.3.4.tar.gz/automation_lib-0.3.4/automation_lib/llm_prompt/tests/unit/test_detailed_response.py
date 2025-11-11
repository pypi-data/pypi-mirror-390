"""
Unit Tests für die detaillierte LLM Response Funktionalität

Diese Tests überprüfen die korrekte Funktionsweise der execute_prompt_detailed Funktion
und der zugehörigen Response-Schemas.
"""

import unittest
from datetime import datetime
from unittest.mock import Mock, patch

from automation_lib.llm_prompt import OpenAIModel, execute_prompt_detailed
from automation_lib.llm_prompt.schemas.llm_response_schemas import LLMResponse, RateLimitInfo, TokenUsage


class TestDetailedResponse(unittest.TestCase):
    """Test cases für detaillierte LLM Responses."""

    def test_llm_response_creation(self):
        """Test der LLMResponse Erstellung mit allen Feldern."""
        token_usage = TokenUsage(
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30
        )
        
        rate_limit_info = RateLimitInfo(
            requests_remaining=100,
            tokens_remaining=5000,
            requests_per_minute=200,
            tokens_per_minute=10000,
            requests_reset_time=datetime.now(),
            tokens_reset_time=datetime.now()
        )
        
        response = LLMResponse(
            content="Test response content",
            model="gpt-4o-mini",
            provider="openai",
            token_usage=token_usage,
            rate_limit_info=rate_limit_info,
            response_time_ms=1500,
            finish_reason="stop",
            request_id="req_123",
            created_at=datetime.now(),
            raw_response={"test": "data"}
        )
        
        self.assertEqual(response.content, "Test response content")
        self.assertEqual(response.model, "gpt-4o-mini")
        self.assertEqual(response.provider, "openai")
        self.assertIsNotNone(response.token_usage)
        if response.token_usage:
            self.assertEqual(response.token_usage.total_tokens, 30)
        self.assertIsNotNone(response.rate_limit_info)
        if response.rate_limit_info:
            self.assertEqual(response.rate_limit_info.requests_remaining, 100)
        self.assertEqual(response.response_time_ms, 1500)

    def test_llm_response_str_representation(self):
        """Test der String-Repräsentation von LLMResponse."""
        response = LLMResponse(
            content="Hello World",
            model="gpt-4o-mini",
            provider="openai",
            token_usage=None,
            rate_limit_info=None,
            response_time_ms=None,
            finish_reason=None,
            request_id=None,
            created_at=None,
            raw_response=None
        )
        
        self.assertEqual(str(response), "Hello World")

    def test_cost_estimate_openai(self):
        """Test der Kostenschätzung für OpenAI Modelle."""
        token_usage = TokenUsage(
            prompt_tokens=500,
            completion_tokens=500,
            total_tokens=1000
        )
        
        response = LLMResponse(
            content="Test",
            model="gpt-4o-mini",
            provider="openai",
            token_usage=token_usage,
            rate_limit_info=None,
            response_time_ms=None,
            finish_reason=None,
            request_id=None,
            created_at=None,
            raw_response=None
        )
        
        cost = response.get_cost_estimate()
        self.assertIsNotNone(cost)
        if cost is not None:
            self.assertAlmostEqual(cost, 0.00015, places=5)  # 1000 tokens * 0.00015 per 1k

    def test_cost_estimate_gemini(self):
        """Test der Kostenschätzung für Gemini Modelle."""
        token_usage = TokenUsage(
            prompt_tokens=1000,
            completion_tokens=1000,
            total_tokens=2000
        )
        
        response = LLMResponse(
            content="Test",
            model="gemini-1.5-flash",
            provider="gemini",
            token_usage=token_usage,
            rate_limit_info=None,
            response_time_ms=None,
            finish_reason=None,
            request_id=None,
            created_at=None,
            raw_response=None
        )
        
        cost = response.get_cost_estimate()
        self.assertIsNotNone(cost)
        if cost is not None:
            self.assertAlmostEqual(cost, 0.0007, places=5)  # 2000 tokens * 0.00035 per 1k

    def test_cost_estimate_no_tokens(self):
        """Test der Kostenschätzung ohne Token-Informationen."""
        response = LLMResponse(
            content="Test",
            model="gpt-4o-mini",
            provider="openai",
            token_usage=None,
            rate_limit_info=None,
            response_time_ms=None,
            finish_reason=None,
            request_id=None,
            created_at=None,
            raw_response=None
        )
        
        cost = response.get_cost_estimate()
        self.assertIsNone(cost)

    def test_is_rate_limited_false(self):
        """Test der Rate Limit Prüfung bei ausreichenden Limits."""
        rate_limit_info = RateLimitInfo(
            requests_remaining=100,
            requests_per_minute=200,
            tokens_remaining=5000,
            tokens_per_minute=10000,
            requests_reset_time=datetime.now(),
            tokens_reset_time=datetime.now()
        )
        
        response = LLMResponse(
            content="Test",
            model="gpt-4o-mini",
            provider="openai",
            token_usage=None,
            rate_limit_info=rate_limit_info,
            response_time_ms=None,
            finish_reason=None,
            request_id=None,
            created_at=None,
            raw_response=None
        )
        
        self.assertFalse(response.is_rate_limited())

    def test_is_rate_limited_true_requests(self):
        """Test der Rate Limit Prüfung bei niedrigen Request-Limits."""
        rate_limit_info = RateLimitInfo(
            requests_remaining=5,  # Nur 5 von 200 übrig = 97.5% verwendet
            requests_per_minute=200,
            tokens_remaining=5000,
            tokens_per_minute=10000,
            requests_reset_time=datetime.now(),
            tokens_reset_time=datetime.now()
        )
        
        response = LLMResponse(
            content="Test",
            model="gpt-4o-mini",
            provider="openai",
            token_usage=None,
            rate_limit_info=rate_limit_info,
            response_time_ms=None,
            finish_reason=None,
            request_id=None,
            created_at=None,
            raw_response=None
        )
        
        self.assertTrue(response.is_rate_limited())

    def test_is_rate_limited_true_tokens(self):
        """Test der Rate Limit Prüfung bei niedrigen Token-Limits."""
        rate_limit_info = RateLimitInfo(
            requests_remaining=100,
            requests_per_minute=200,
            tokens_remaining=500,  # Nur 500 von 10000 übrig = 95% verwendet
            tokens_per_minute=10000,
            requests_reset_time=datetime.now(),
            tokens_reset_time=datetime.now()
        )
        
        response = LLMResponse(
            content="Test",
            model="gpt-4o-mini",
            provider="openai",
            token_usage=None,
            rate_limit_info=rate_limit_info,
            response_time_ms=None,
            finish_reason=None,
            request_id=None,
            created_at=None,
            raw_response=None
        )
        
        self.assertTrue(response.is_rate_limited())

    def test_is_rate_limited_no_info(self):
        """Test der Rate Limit Prüfung ohne Rate Limit Informationen."""
        response = LLMResponse(
            content="Test",
            model="gpt-4o-mini",
            provider="openai",
            token_usage=None,
            rate_limit_info=None,
            response_time_ms=None,
            finish_reason=None,
            request_id=None,
            created_at=None,
            raw_response=None
        )
        
        self.assertFalse(response.is_rate_limited())

    @patch('automation_lib.llm_prompt.llm_prompt_runner.LLMProviderFactory.create_provider')
    def test_execute_prompt_detailed_integration(self, mock_create_provider):
        """Test der execute_prompt_detailed Funktion mit Mock Provider."""
        # Mock Provider Setup
        mock_provider = Mock()
        mock_response = LLMResponse(
            content="Mocked response",
            model="gpt-4o-mini",
            provider="openai",
            token_usage=TokenUsage(prompt_tokens=5, completion_tokens=10, total_tokens=15),
            rate_limit_info=None,
            response_time_ms=1000,
            finish_reason=None,
            request_id=None,
            created_at=None,
            raw_response=None
        )
        mock_provider.execute_prompt_detailed_with_fallback.return_value = mock_response
        mock_create_provider.return_value = mock_provider
        
        # Test der Funktion
        result = execute_prompt_detailed(
            prompt="Test prompt",
            model=OpenAIModel.GPT_4O_MINI
        )
        
        # Assertions
        self.assertIsInstance(result, LLMResponse)
        self.assertEqual(result.content, "Mocked response")
        self.assertEqual(result.model, "gpt-4o-mini")
        self.assertIsNotNone(result.token_usage)
        if result.token_usage:
            self.assertEqual(result.token_usage.total_tokens, 15)
        
        # Verify mock calls
        mock_create_provider.assert_called_once()
        mock_provider.execute_prompt_detailed_with_fallback.assert_called_once()


if __name__ == '__main__':
    unittest.main()
