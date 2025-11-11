"""
Vision Example

This example demonstrates how to use the LLM Prompt module with image inputs
for vision-based tasks like image analysis, OCR, and visual question answering.
"""

import os

from automation_lib.llm_prompt import (
    GeminiModel,
    OpenAIModel,
    execute_prompt_with_images,
    execute_prompt_with_images_detailed,
)
from automation_lib.utils.image_schemas import image_from_file, image_from_url


def analyze_image_from_file():
    """
    Example: Analyze an image from a local file.
    """
    print("=== Analyzing Image from File ===")
    
    # Create an ImageInput from a local file
    # Note: Replace with an actual image path
    image_path = "path/to/your/image.jpg"
    
    if not os.path.exists(image_path):
        print(f"Image file not found: {image_path}")
        print("Please provide a valid image path to test this example.")
        return
    
    try:
        # Create ImageInput from file
        image_input = image_from_file(image_path)

        # Analyze the image
        prompt = "What do you see in this image? Describe it in detail."
        
        # Use GPT-4o for vision analysis
        response = execute_prompt_with_images(
            prompt=prompt,
            images=[image_input],
            model=OpenAIModel.GPT_4O
        )
        
        print(f"Analysis: {response}")
        
    except Exception as e:
        print(f"Error analyzing image: {e}")


def analyze_image_from_url():
    """
    Example: Analyze an image from a URL.
    """
    print("\n=== Analyzing Image from URL ===")
    
    # Example with a public image URL
    image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
    
    try:
        # Create ImageInput from URL
        image_input = image_from_url(image_url)

        # Analyze the image
        prompt = "What type of landscape is shown in this image? What are the main features?"

        # Use Gemini for vision analysis
        response = execute_prompt_with_images(
            prompt=prompt,
            images=[image_input],
            model=GeminiModel.GEMINI_2_0_FLASH
        )
        
        print(f"Analysis: {response}")
        
    except Exception as e:
        print(f"Error analyzing image from URL: {e}")


def analyze_image_with_detailed_response():
    """
    Example: Get detailed response with metadata when analyzing an image.
    """
    print("\n=== Detailed Vision Analysis ===")
    
    # Example with a public image URL
    image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/280px-PNG_transparency_demonstration_1.png"
    
    try:
        # Create ImageInput from URL
        image_input = image_from_url(image_url)

        # Analyze the image with detailed response
        prompt = "Describe this image and identify any text or symbols you can see."
        
        detailed_response = execute_prompt_with_images_detailed(
            prompt=prompt,
            images=[image_input],
            model=OpenAIModel.GPT_4O,
            temperature=0.3
        )
        
        print(f"Content: {detailed_response.content}")
        print(f"Model: {detailed_response.model}")
        print(f"Provider: {detailed_response.provider}")
        print(f"Response Time: {detailed_response.response_time_ms}ms")
        
        if detailed_response.token_usage:
            print(f"Token Usage: {detailed_response.token_usage.total_tokens} total tokens")
            print(f"  - Prompt: {detailed_response.token_usage.prompt_tokens}")
            print(f"  - Completion: {detailed_response.token_usage.completion_tokens}")
        
    except Exception as e:
        print(f"Error in detailed vision analysis: {e}")


def analyze_multiple_images():
    """
    Example: Analyze multiple images in a single prompt.
    """
    print("\n=== Analyzing Multiple Images ===")
    
    # Example with multiple public image URLs
    image_urls = [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Vd-Orig.png/256px-Vd-Orig.png",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Google_2015_logo.svg/272px-Google_2015_logo.svg.png"
    ]
    
    try:
        # Create ImageInput objects from URLs
        image_inputs = [image_from_url(url) for url in image_urls]

        # Compare the images
        prompt = "Compare these two images. What are the differences and similarities? What do they represent?"

        response = execute_prompt_with_images(
            prompt=prompt,
            images=image_inputs,
            model=GeminiModel.GEMINI_2_0_PRO
        )
        
        print(f"Comparison: {response}")
        
    except Exception as e:
        print(f"Error analyzing multiple images: {e}")


def ocr_example():
    """
    Example: Extract text from an image (OCR).
    """
    print("\n=== OCR Example ===")
    
    # Example with an image containing text
    image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Banana-Single.jpg/272px-Banana-Single.jpg"
    
    try:
        # Create ImageInput from URL
        image_input = image_from_url(image_url)

        # Extract text from the image
        prompt = "Extract any text visible in this image. If there's no text, describe what you see instead."
        
        response = execute_prompt_with_images(
            prompt=prompt,
            images=[image_input],
            model=OpenAIModel.GPT_4O_MINI,
            temperature=0.1  # Low temperature for more consistent OCR
        )
        
        print(f"OCR Result: {response}")
        
    except Exception as e:
        print(f"Error in OCR: {e}")


def vision_with_system_prompt():
    """
    Example: Use vision with a system prompt for specialized analysis.
    """
    print("\n=== Vision with System Prompt ===")
    
    # Example image URL
    image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
    
    try:
        # Create ImageInput from URL
        image_input = image_from_url(image_url)

        # Use a system prompt to set the context
        system_prompt = """You are a professional landscape photographer and nature guide.
        When analyzing images, focus on:
        1. Composition and photographic techniques
        2. Natural elements and their ecological significance
        3. Potential improvements or interesting aspects
        Provide detailed, professional insights."""

        prompt = "Analyze this landscape photograph from a professional perspective."

        response = execute_prompt_with_images(
            prompt=prompt,
            images=[image_input],
            model=GeminiModel.GEMINI_2_0_PRO,
            system_prompt=system_prompt,
            temperature=0.7
        )
        
        print(f"Professional Analysis: {response}")
        
    except Exception as e:
        print(f"Error in professional analysis: {e}")


def vision_with_custom_config():
    """
    Example: Use vision with custom configuration.
    """
    print("\n=== Vision with Custom Config ===")
    
    # Example image URL
    image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Google_2015_logo.svg/272px-Google_2015_logo.svg.png"

    try:
        # Create ImageInput from URL
        image_input = image_from_url(image_url)

        prompt = "Describe this logo in exactly 3 sentences. Focus on design elements and brand recognition."

        response = execute_prompt_with_images(
            prompt=prompt,
            images=[image_input],
            model=OpenAIModel.GPT_4O,
            temperature=0.5,
            max_tokens=500
        )
        
        print(f"Logo Analysis: {response}")
        
    except Exception as e:
        print(f"Error with custom config: {e}")


if __name__ == "__main__":
    print("LLM Prompt Vision Examples")
    print("=" * 50)
    
    # Run examples that work with public URLs
    analyze_image_from_url()
    analyze_image_with_detailed_response()
    analyze_multiple_images()
    ocr_example()
    vision_with_system_prompt()
    vision_with_custom_config()
    
    # Note: File-based example requires a local image
    # analyze_image_from_file()
    
    print("\n" + "=" * 50)
    print("Vision examples completed!")
    print("\nNote: To test with local images, uncomment and modify the")
    print("analyze_image_from_file() function with a valid image path.")
