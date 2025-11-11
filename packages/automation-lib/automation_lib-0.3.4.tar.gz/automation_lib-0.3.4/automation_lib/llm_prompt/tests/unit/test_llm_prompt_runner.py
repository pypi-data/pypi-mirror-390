import unittest
from unittest.mock import MagicMock, patch

from automation_lib.llm_prompt.llm_prompt_helpers import validate_prompt_input
from automation_lib.llm_prompt.llm_prompt_runner import execute_prompt


class TestLLMPromptRunner(unittest.TestCase):

    def setUp(self):
        # Patch LLMPromptConfig in the runner module where it's imported
        self.mock_llm_prompt_config_patcher = patch('automation_lib.llm_prompt.llm_prompt_runner.LLMPromptConfig')
        self.mock_llm_prompt_config_class = self.mock_llm_prompt_config_patcher.start()

        self.mock_config_instance = MagicMock()
        self.mock_config_instance.model_name = "mock-default-model"
        self.mock_config_instance.openai_api_key = "mock_openai_key"
        self.mock_config_instance.gemini_api_key = "mock_gemini_key"
        self.mock_config_instance.temperature = 0.7
        self.mock_config_instance.max_tokens = None
        self.mock_config_instance.timeout = 60
        
        # When LLMPromptConfig() is called, return our mock instance
        self.mock_llm_prompt_config_class.return_value = self.mock_config_instance

        # Patch the LLMProviderFactory
        self.mock_provider_factory_patcher = patch('automation_lib.llm_prompt.llm_prompt_runner.LLMProviderFactory')
        self.mock_provider_factory_class = self.mock_provider_factory_patcher.start()
        self.mock_provider_instance = MagicMock()
        self.mock_provider_factory_class.create_provider.return_value = self.mock_provider_instance

    def tearDown(self):
        self.mock_llm_prompt_config_patcher.stop()
        self.mock_provider_factory_patcher.stop()

    def test_execute_prompt_success(self):
        # Mock the detailed response object
        mock_detailed_response = MagicMock()
        mock_detailed_response.content = "Mocked LLM response."
        self.mock_provider_instance.execute_prompt_detailed_with_fallback.return_value = mock_detailed_response

        prompt = "Hello, LLM!"
        response = execute_prompt(prompt=prompt)

        self.mock_provider_factory_class.create_provider.assert_called_once_with(
            "mock-default-model", self.mock_config_instance
        )
        self.mock_provider_instance.execute_prompt_detailed_with_fallback.assert_called_once_with(
            prompt, model="mock-default-model", fallback_models=[], system_prompt=None,
        )
        self.assertEqual(response, "Mocked LLM response.")

    def test_execute_prompt_with_override_args(self):
        # Mock the detailed response object
        mock_detailed_response = MagicMock()
        mock_detailed_response.content = "Overridden response."
        self.mock_provider_instance.execute_prompt_detailed_with_fallback.return_value = mock_detailed_response

        prompt = "Test override."
        model = "gpt-4o-mini"
        temperature = 0.9
        max_tokens = 50
        timeout = 120

        response = execute_prompt(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout
        )

        self.mock_provider_factory_class.create_provider.assert_called_once_with(
            model, self.mock_config_instance
        )
        # The ModelResolver now adds default fallbacks for known models
        expected_fallback_models = ["gpt-3.5-turbo"] if model == "gpt-4o-mini" else []
        self.mock_provider_instance.execute_prompt_detailed_with_fallback.assert_called_once_with(
            prompt,
            model=model,
            fallback_models=expected_fallback_models,
            system_prompt=None,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout
        )
        self.assertEqual(response, "Overridden response.")

    def test_execute_prompt_api_error(self):
        self.mock_provider_instance.execute_prompt_detailed_with_fallback.side_effect = Exception("API call failed.")

        with self.assertRaisesRegex(Exception, "API call failed."):
            execute_prompt(prompt="This should fail.")

class TestLLMPromptHelpers(unittest.TestCase):

    def test_validate_prompt_input_valid(self):
        validate_prompt_input("Valid prompt", "valid-model")
        # No exception means success

    def test_validate_prompt_input_empty_prompt(self):
        with self.assertRaisesRegex(ValueError, "Prompt cannot be empty."):
            validate_prompt_input("", "valid-model")

    def test_validate_prompt_input_whitespace_prompt(self):
        with self.assertRaisesRegex(ValueError, "Prompt cannot be empty."):
            validate_prompt_input("   ", "valid-model")

    def test_validate_prompt_input_empty_model(self):
        with self.assertRaisesRegex(ValueError, "Model name cannot be empty."):
            validate_prompt_input("Valid prompt", "")

    def test_validate_prompt_input_whitespace_model(self):
        with self.assertRaisesRegex(ValueError, "Model name cannot be empty."):
            validate_prompt_input("Valid prompt", "   ")
