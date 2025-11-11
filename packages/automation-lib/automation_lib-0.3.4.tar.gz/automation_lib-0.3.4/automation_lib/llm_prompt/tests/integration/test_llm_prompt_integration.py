import unittest

from automation_lib.llm_prompt.config.llm_prompt_config import LLMPromptConfig
from automation_lib.llm_prompt.llm_prompt_runner import execute_prompt_detailed
from automation_lib.llm_prompt.models import GeminiModel
from tests.test_utils import (
    check_gemini_api_key_set,
    check_openai_api_key_set,
    skip_unless_integration_test,
)


@skip_unless_integration_test
class TestLLMPromptIntegration(unittest.TestCase):

    def setUp(self):
        self.config = LLMPromptConfig()

    @unittest.skipUnless(
        check_openai_api_key_set(),
        "OpenAI integration tests require OPENAI_API_KEY to be set."
    )
    def test_execute_prompt_openai_integration(self):
        prompt = "Say 'Hello, OpenAI!' and nothing else."
        model = "gpt-4o-mini"

        print(f"\nRunning OpenAI integration test with model: {model}")
        response = execute_prompt_detailed(prompt=prompt, model=model, config=self.config)
        print(f"OpenAI Response: {response}")

        from automation_lib.llm_prompt.schemas.llm_response_schemas import (
            LLMResponse,
            TokenUsage,
        )

        self.assertIsInstance(response, LLMResponse)
        self.assertIsInstance(response.content, str)
        self.assertGreater(len(response.content), 0)
        self.assertIn("hello, openai!", response.content.lower())
        self.assertLess(len(response.content), 50)
        self.assertEqual(response.model, model)
        self.assertEqual(response.provider, "openai")
        self.assertIsInstance(response.token_usage, TokenUsage)
        if response.token_usage:
            if response.token_usage.prompt_tokens is not None:
                prompt_tokens = response.token_usage.prompt_tokens
                self.assertIsInstance(prompt_tokens, int)
            if response.token_usage.completion_tokens is not None:
                completion_tokens = response.token_usage.completion_tokens
                self.assertIsInstance(completion_tokens, int)
            if response.token_usage.total_tokens is not None:
                total_tokens = response.token_usage.total_tokens
                self.assertIsInstance(total_tokens, int)
                self.assertGreaterEqual(total_tokens, 0)
        if response.response_time_ms is not None:
            response_time_ms = response.response_time_ms
            self.assertIsInstance(response_time_ms, int)
            self.assertGreater(response_time_ms, 0)
        self.assertIsNotNone(response.finish_reason)
        self.assertIsNotNone(response.raw_response)

    @unittest.skipUnless(
        check_gemini_api_key_set(),
        "Gemini integration tests require GEMINI_API_KEY to be set."
    )
    def test_execute_prompt_gemini_integration(self):
        prompt = "Say 'Hello, Gemini Flash Preview!' and nothing else."
        model = GeminiModel.GEMINI_2_0_FLASH_LITE # Updated to a more common Gemini model name

        print(f"\nRunning Gemini Flash Preview integration test with model: {model}")
        response = execute_prompt_detailed(prompt=prompt, model=model, max_token=100, config=self.config)
        print(f"Gemini Flash Preview Response: {response}")

        from automation_lib.llm_prompt.schemas.llm_response_schemas import (
            LLMResponse,
            TokenUsage,
        )

        self.assertIsInstance(response, LLMResponse)
        self.assertIsInstance(response.content, str)
        self.assertGreater(len(response.content), 0)
        self.assertIn("hello, gemini flash preview!", response.content.lower())
        self.assertLess(len(response.content), 50)
        self.assertEqual(response.model, model.model_name)
        self.assertEqual(response.provider, "gemini")
        self.assertIsInstance(response.token_usage, TokenUsage)
        if response.token_usage:
            if response.token_usage.prompt_tokens is not None:
                prompt_tokens = response.token_usage.prompt_tokens
                self.assertIsInstance(prompt_tokens, int)
            if response.token_usage.completion_tokens is not None:
                completion_tokens = response.token_usage.completion_tokens
                self.assertIsInstance(completion_tokens, int)
            if response.token_usage.total_tokens is not None:
                total_tokens = response.token_usage.total_tokens
                self.assertIsInstance(total_tokens, int)
                self.assertGreaterEqual(total_tokens, 0)
        if response.response_time_ms is not None:
            response_time_ms = response.response_time_ms
            self.assertIsInstance(response_time_ms, int)
            self.assertGreater(response_time_ms, 0)
        self.assertIsNotNone(response.finish_reason)
        self.assertIsNotNone(response.raw_response)

    @skip_unless_integration_test
    def test_execute_prompt_invalid_model_integration(self):
        prompt = "This should fail."
        model = "invalid-model-for-testing-123"

        print(f"\nRunning invalid model integration test with model: {model}")
        with self.assertRaises(ValueError) as cm: # Expecting ValueError from our factory
            execute_prompt_detailed(prompt=prompt, model=model, config=self.config)
        self.assertIn("No suitable LLM provider found for model", str(cm.exception))
        print("Caught expected exception for invalid model.")
