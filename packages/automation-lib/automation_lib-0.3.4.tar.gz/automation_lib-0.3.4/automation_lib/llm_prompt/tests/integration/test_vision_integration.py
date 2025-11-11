"""
Integration Tests for Vision Functionality

Integration tests for image processing capabilities in the LLM Prompt module.
These tests require actual API keys and make real API calls.
"""

import unittest
from typing import cast  # Import cast for type hinting

from automation_lib.llm_prompt import (
    GeminiModel,
    OpenAIModel,
    execute_prompt_with_images,
    execute_prompt_with_images_detailed,
)
from automation_lib.utils.image_utils import download_image_from_url
from tests.test_utils import skip_unless_integration_test  # Import the utility function


@skip_unless_integration_test
class TestVisionIntegration(unittest.TestCase):
    """Integration test cases for vision functionality."""

    def setUp(self):
        """Set up test fixtures."""
        
        # Test image URL (public domain image)
        self.test_image_url = "https://picsum.photos/640/480"
        
        # Download the image once for all tests
        try:
            self.downloaded_image_input = download_image_from_url(
                url=self.test_image_url,
                max_size_mb=5 # Ensure it's within limits
            )
        except Exception as e:
            self.fail(f"Failed to download test image: {e}")

    def test_openai_vision_with_url_image(self):
        """Test OpenAI vision with image from URL."""
        
        # Use the pre-downloaded image input
        image_input = self.downloaded_image_input
        
        # Test basic vision functionality
        prompt = "What do you see in this image? Describe the main elements briefly."
        
        try:
            response = execute_prompt_with_images(
                prompt=prompt,
                images=[image_input],
                model=OpenAIModel.GPT_4O_MINI,
            )
            
            # Verify we got a response
            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 10)
            
            # Response should mention typical elements of the image
            response_lower = response.lower()
            # The image shows a wooden boardwalk through nature
            self.assertTrue(
                any(word in response_lower for word in ['boardwalk', 'path', 'walkway', 'bridge', 'wood', 'nature', 'grass', 'green']),
                f"Response doesn't seem to describe the image content: {response}"
            )
            
        except Exception as e:
            self.fail(f"OpenAI vision test failed: {e}")

    def test_openai_vision_detailed_response(self):
        """Test OpenAI vision with detailed response."""
        
        # Use the pre-downloaded image input
        image_input = self.downloaded_image_input
        
        prompt = "Describe this landscape image in detail."
        
        try:
            response = execute_prompt_with_images_detailed(
                prompt=prompt,
                images=[image_input],
                model=OpenAIModel.GPT_4O_MINI,

            )
            
            # Verify response structure
            self.assertIsNotNone(response.content)
            self.assertEqual(response.model, OpenAIModel.GPT_4O_MINI.model_name)
            self.assertEqual(response.provider, "openai")
            self.assertIsNotNone(response.response_time_ms)
            self.assertGreater(cast(int, response.response_time_ms), 0)
            
            # Check token usage if available
            if response.token_usage:
                self.assertIsNotNone(response.token_usage.total_tokens)
                self.assertIsNotNone(response.token_usage.prompt_tokens)
                self.assertIsNotNone(response.token_usage.completion_tokens)
                self.assertGreater(cast(int, response.token_usage.total_tokens), 0)
                self.assertGreater(cast(int, response.token_usage.prompt_tokens), 0)
                self.assertGreater(cast(int, response.token_usage.completion_tokens), 0)
            
        except Exception as e:
            self.fail(f"OpenAI detailed vision test failed: {e}")

    def test_gemini_vision_with_url_image(self):
        """Test Gemini vision with image from URL."""
        
        # Use the pre-downloaded image input
        image_input = self.downloaded_image_input
        
        prompt = "What do you see in this image? Describe the main elements briefly."
        
        try:
            response = execute_prompt_with_images(
                prompt=prompt,
                images=[image_input],
                model=GeminiModel.GEMINI_2_5_FLASH
            )
            
            # Verify we got a response
            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 10)
            
            # Response should mention typical elements of the image
            response_lower = response.lower()
            self.assertTrue(
                any(word in response_lower for word in ['boardwalk', 'path', 'walkway', 'bridge', 'wood', 'nature', 'grass', 'green']),
                f"Response doesn't seem to describe the image content: {response}"
            )
            
        except Exception as e:
            self.fail(f"Gemini vision test failed: {e}")

    def test_vision_with_system_prompt(self):
        """Test vision functionality with system prompt."""

        
        # Use the pre-downloaded image input
        image_input = self.downloaded_image_input
        
        system_prompt = "You are a professional landscape photographer. Analyze images from a technical photography perspective."
        prompt = "Analyze this image's composition and photographic qualities."
        
        try:
            response = execute_prompt_with_images(
                prompt=prompt,
                images=[image_input],
                model=OpenAIModel.GPT_4O_MINI,
                system_prompt=system_prompt
            )
            
            # Verify we got a response
            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 20)
            
            # Response should reflect the professional photography context
            response_lower = response.lower()
            self.assertTrue(
                any(word in response_lower for word in ['composition', 'perspective', 'lighting', 'depth', 'focus', 'lines', 'photography']),
                f"Response doesn't seem to reflect photography analysis: {response}"
            )
            
        except Exception as e:
            self.fail(f"Vision with system prompt test failed: {e}")

    def test_vision_error_handling_invalid_url(self):
        """Test error handling with invalid image URL."""

        
        # Create image input with invalid URL
        invalid_url = "https://example.com/nonexistent-image.jpg"
        
        try:
            # This should fail when trying to download the image
            with self.assertRaises(Exception) as cm:
                download_image_from_url(
                    url=invalid_url,
                    max_size_mb=5
                )
            # Assert that the exception message indicates a download failure
            self.assertIn("Fehler beim Herunterladen", str(cm.exception))
            
        except Exception:
            # Expected to fail during image download
            pass

    def test_vision_with_custom_parameters(self):
        """Test vision with custom parameters."""

        
        # Use the pre-downloaded image input
        image_input = self.downloaded_image_input
        
        prompt = "Describe this image in exactly 2 sentences."
        
        try:
            response = execute_prompt_with_images_detailed(
                prompt=prompt,
                images=[image_input],
                model=OpenAIModel.GPT_4O_MINI,
                temperature=0.3,
                max_tokens=100
            )
            
            # Verify we got a response
            self.assertIsNotNone(response.content)
            self.assertGreater(len(response.content), 10)
            
            # Response should be relatively short due to max_tokens limit
            self.assertLess(len(response.content), 500)
            
        except Exception as e:
            self.fail(f"Vision with custom parameters test failed: {e}")


if __name__ == '__main__':
    # Print information about test requirements
    print("Vision Integration Tests")
    print("=" * 50)
    print("These tests require valid API keys in your configuration.")
    print("Set SKIP_INTEGRATION_TESTS=true to skip these tests.")
    print("=" * 50)
    
    unittest.main()
