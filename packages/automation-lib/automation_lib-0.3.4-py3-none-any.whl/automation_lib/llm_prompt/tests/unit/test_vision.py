"""
Unit Tests for Vision Functionality

Tests for image processing capabilities in the LLM Prompt module.
"""

import unittest
from datetime import datetime
from unittest.mock import Mock, patch

from automation_lib.llm_prompt.config.llm_prompt_config import LLMPromptConfig
from automation_lib.llm_prompt.llm_prompt_runner import execute_prompt_with_images, execute_prompt_with_images_detailed
from automation_lib.llm_prompt.models import GeminiModel, OpenAIModel
from automation_lib.llm_prompt.schemas.llm_response_schemas import LLMResponse, TokenUsage
from automation_lib.utils.image_schemas import ImageInput


class TestVisionFunctionality(unittest.TestCase):
    """Test cases for vision functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_prompt = "What do you see in this image?"
        self.test_image_data = b"fake_image_data"
        self.mock_config = LLMPromptConfig.default()

    def test_image_input_creation_with_bytes(self):
        """Test creating ImageInput with bytes data."""
        image_input = ImageInput(
            source=self.test_image_data,
            mime_type="image/jpeg",
            description="Test image",
            max_size_mb=10
        )
        
        self.assertEqual(image_input.source, self.test_image_data)
        self.assertEqual(image_input.mime_type, "image/jpeg")

    def test_image_input_creation_with_url(self):
        """Test creating ImageInput with URL."""
        test_url = "https://example.com/image.jpg"
        
        with patch('automation_lib.llm_prompt.image_utils.download_image_from_url') as mock_download:
            mock_download.return_value = self.test_image_data
            
            image_input = ImageInput(
                source=test_url,
                mime_type="image/jpeg",
                description="Test image from URL",
                max_size_mb=10
            )
            
            self.assertEqual(image_input.source, test_url)
            self.assertEqual(image_input.mime_type, "image/jpeg")

    def test_image_input_to_bytes(self):
        """Test converting ImageInput to bytes."""
        image_input = ImageInput(
            source=self.test_image_data,
            mime_type="image/jpeg",
            description="Test image",
            max_size_mb=10
        )
        
        result_bytes = image_input.to_bytes()
        self.assertEqual(result_bytes, self.test_image_data)

    @patch('automation_lib.llm_prompt.llm_prompt_runner.LLMProviderFactory.create_provider')
    @patch('automation_lib.llm_prompt.llm_prompt_runner.ModelResolver.resolve_model')
    def test_execute_prompt_with_images_success(self, mock_resolve, mock_factory):
        """Test successful execution of prompt with images."""
        # Setup mocks
        mock_resolve.return_value = (OpenAIModel.GPT_4O.model_name, [])
        
        mock_provider = Mock()
        mock_provider.supports_vision.return_value = True
        mock_provider.get_vision_models.return_value = [OpenAIModel.GPT_4O.model_name]
        mock_provider.execute_prompt_with_images_detailed_with_fallback.return_value = LLMResponse(
            content="I see a test image",
            model=OpenAIModel.GPT_4O.model_name,
            provider="openai",
            token_usage=TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            rate_limit_info=None,
            response_time_ms=1000,
            finish_reason="stop",
            request_id="test-123",
            created_at=datetime.now(),
            raw_response={}
        )
        mock_factory.return_value = mock_provider
        
        # Create test image
        image_input = ImageInput(
            source=self.test_image_data,
            mime_type="image/jpeg",
            description="Test image",
            max_size_mb=10
        )
        
        # Execute test
        result = execute_prompt_with_images(
            prompt=self.test_prompt,
            images=[image_input],
            model=OpenAIModel.GPT_4O
        )
        
        # Verify results
        self.assertEqual(result, "I see a test image")
        mock_provider.execute_prompt_with_images_detailed_with_fallback.assert_called_once()

    @patch('automation_lib.llm_prompt.llm_prompt_runner.LLMProviderFactory.create_provider')
    @patch('automation_lib.llm_prompt.llm_prompt_runner.ModelResolver.resolve_model')
    def test_execute_prompt_with_images_detailed_success(self, mock_resolve, mock_factory):
        """Test successful execution of detailed prompt with images."""
        # Setup mocks
        mock_resolve.return_value = (GeminiModel.GEMINI_2_5_FLASH.model_name, [])
        
        mock_provider = Mock()
        mock_provider.supports_vision.return_value = True
        mock_provider.get_vision_models.return_value = [GeminiModel.GEMINI_2_5_FLASH.model_name]
        
        expected_response = LLMResponse(
            content="Detailed image analysis",
            model=GeminiModel.GEMINI_2_5_FLASH.model_name,
            provider="gemini",
            token_usage=TokenUsage(prompt_tokens=15, completion_tokens=25, total_tokens=40),
            rate_limit_info=None,
            response_time_ms=1500,
            finish_reason="stop",
            request_id="test-456",
            created_at=datetime.now(),
            raw_response={}
        )
        mock_provider.execute_prompt_with_images_detailed_with_fallback.return_value = expected_response
        mock_factory.return_value = mock_provider
        
        # Create test image
        image_input = ImageInput(
            source=self.test_image_data,
            mime_type="image/jpeg",
            description="Test image",
            max_size_mb=10
        )
        
        # Execute test
        result = execute_prompt_with_images_detailed(
            prompt=self.test_prompt,
            images=[image_input],
            model=GeminiModel.GEMINI_2_5_FLASH, # Changed to enum member
            config=self.mock_config
        )
        
        # Verify results
        self.assertEqual(result, expected_response)
        self.assertEqual(result.content, "Detailed image analysis")
        self.assertEqual(result.model, GeminiModel.GEMINI_2_5_FLASH.model_name)
        if result.token_usage is None:
            self.fail("Token usage should not be None")
            
        self.assertEqual(result.token_usage.total_tokens, 40)

    @patch('automation_lib.llm_prompt.llm_prompt_runner.LLMProviderFactory.create_provider')
    @patch('automation_lib.llm_prompt.llm_prompt_runner.ModelResolver.resolve_model')
    def test_execute_prompt_with_images_no_vision_support(self, mock_resolve, mock_factory):
        """Test error when provider doesn't support vision."""
        # Setup mocks
        mock_resolve.return_value = ("text-model", [])
        
        mock_provider = Mock()
        mock_provider.supports_vision.return_value = False
        mock_factory.return_value = mock_provider
        
        # Create test image
        image_input = ImageInput(
            source=self.test_image_data,
            mime_type="image/jpeg",
            description="Test image",
            max_size_mb=10
        )
        
        # Execute test and expect error
        with self.assertRaises(ValueError) as context:
            execute_prompt_with_images(
                prompt=self.test_prompt,
                images=[image_input],
                model="text-model"
            )
        
        self.assertIn("does not support vision", str(context.exception))

    def test_execute_prompt_with_images_no_images_provided(self):
        """Test error when no images are provided."""
        with self.assertRaises(ValueError) as context:
            execute_prompt_with_images(
                prompt=self.test_prompt,
                images=[],
                model=OpenAIModel.GPT_4O
            )
        
        self.assertIn("At least one image must be provided", str(context.exception))

    @patch('automation_lib.llm_prompt.llm_prompt_runner.LLMProviderFactory.create_provider')
    @patch('automation_lib.llm_prompt.llm_prompt_runner.ModelResolver.resolve_model')
    def test_execute_prompt_with_images_model_fallback(self, mock_resolve, mock_factory):
        """Test fallback to vision-capable model when primary doesn't support vision."""
        # Setup mocks - primary model doesn't support vision, fallback does
        mock_resolve.return_value = ("text-model", [OpenAIModel.GPT_4O.model_name])
        
        mock_provider = Mock()
        mock_provider.supports_vision.return_value = True
        mock_provider.get_vision_models.return_value = [OpenAIModel.GPT_4O.model_name]
        mock_provider.execute_prompt_with_images_detailed_with_fallback.return_value = LLMResponse(
            content="Fallback vision analysis",
            model=OpenAIModel.GPT_4O.model_name,
            provider="openai",
            token_usage=TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15), # Added TokenUsage
            rate_limit_info=None,
            response_time_ms=1200,
            finish_reason="stop",
            request_id="test-789",
            created_at=datetime.now(),
            raw_response={}
        )
        mock_factory.return_value = mock_provider
        
        # Create test image
        image_input = ImageInput(
            source=self.test_image_data,
            mime_type="image/jpeg",
            description="Test image",
            max_size_mb=10
        )
        
        # Execute test
        result = execute_prompt_with_images(
            prompt=self.test_prompt,
            images=[image_input],
            model="text-model"
        )
        
        # Verify fallback was used
        self.assertEqual(result, "Fallback vision analysis")
        mock_provider.execute_prompt_with_images_detailed_with_fallback.assert_called_once()

    @patch('automation_lib.llm_prompt.llm_prompt_runner.LLMProviderFactory.create_provider')
    @patch('automation_lib.llm_prompt.llm_prompt_runner.ModelResolver.resolve_model')
    def test_execute_prompt_with_multiple_images(self, mock_resolve, mock_factory):
        """Test execution with multiple images."""
        # Setup mocks
        mock_resolve.return_value = (OpenAIModel.GPT_4O.model_name, [])
        
        mock_provider = Mock()
        mock_provider.supports_vision.return_value = True
        mock_provider.get_vision_models.return_value = [OpenAIModel.GPT_4O.model_name]
        mock_provider.execute_prompt_with_images_detailed_with_fallback.return_value = LLMResponse(
            content="Analysis of multiple images",
            model=OpenAIModel.GPT_4O.model_name,
            provider="openai",
            token_usage=TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            rate_limit_info=None,
            response_time_ms=2000,
            finish_reason="stop",
            request_id="test-multi",
            created_at=datetime.now(),
            raw_response={}
        )
        mock_factory.return_value = mock_provider
        
        # Create test images
        image1 = ImageInput(
            source=b"image1_data",
            mime_type="image/jpeg",
            description="First test image",
            max_size_mb=10
        )
        
        image2 = ImageInput(
            source=b"image2_data",
            mime_type="image/png",
            description="Second test image",
            max_size_mb=10
        )
        
        # Execute test
        result = execute_prompt_with_images(
            prompt="Compare these images",
            images=[image1, image2],
            model=OpenAIModel.GPT_4O
        )
        
        # Verify results
        self.assertEqual(result, "Analysis of multiple images")
        
        # Verify the provider was called with both images
        call_args = mock_provider.execute_prompt_with_images_detailed_with_fallback.call_args
        self.assertEqual(len(call_args[0][1]), 2)  # Second argument should be images list with 2 items

    @patch('automation_lib.llm_prompt.llm_prompt_runner.LLMProviderFactory.create_provider')
    @patch('automation_lib.llm_prompt.llm_prompt_runner.ModelResolver.resolve_model')
    def test_execute_prompt_with_images_with_system_prompt(self, mock_resolve, mock_factory):
        """Test execution with system prompt."""
        # Setup mocks
        mock_resolve.return_value = (GeminiModel.GEMINI_2_5_FLASH.model_name, [])
        
        mock_provider = Mock()
        mock_provider.supports_vision.return_value = True
        mock_provider.get_vision_models.return_value = [GeminiModel.GEMINI_2_5_FLASH.model_name]
        mock_provider.execute_prompt_with_images_detailed_with_fallback.return_value = LLMResponse(
            content="Professional image analysis",
            model=GeminiModel.GEMINI_2_5_FLASH.model_name,
            provider="gemini",
            token_usage=TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15), # Added TokenUsage
            rate_limit_info=None,
            response_time_ms=1800,
            finish_reason="stop",
            request_id="test-system",
            created_at=datetime.now(),
            raw_response={}
        )
        mock_factory.return_value = mock_provider
        
        # Create test image
        image_input = ImageInput(
            source=self.test_image_data,
            mime_type="image/jpeg",
            description="Test image",
            max_size_mb=10
        )
        
        system_prompt = "You are a professional image analyst."
        
        # Execute test
        result = execute_prompt_with_images(
            prompt=self.test_prompt,
            images=[image_input],
            model=GeminiModel.GEMINI_2_5_FLASH, # Changed to enum member
            system_prompt=system_prompt
        )
        
        # Verify results
        self.assertEqual(result, "Professional image analysis")
        
        # Verify system prompt was passed
        call_args = mock_provider.execute_prompt_with_images_detailed_with_fallback.call_args
        self.assertEqual(call_args[1]['system_prompt'], system_prompt)


if __name__ == '__main__':
    unittest.main()
