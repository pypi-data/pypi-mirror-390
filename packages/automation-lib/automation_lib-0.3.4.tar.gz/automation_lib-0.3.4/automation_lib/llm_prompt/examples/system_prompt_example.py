"""
System Prompt Example

Demonstrates how to use system prompts with different LLM providers.
"""

from automation_lib.llm_prompt.llm_prompt_runner import execute_prompt
from automation_lib.llm_prompt.models import GeminiModel, OpenAIModel


def main():
    """Demonstrate system prompt usage with different providers."""
    
    # Example 1: Using system prompt with OpenAI
    print("=== OpenAI Example with System Prompt ===")
    try:
        system_prompt = "Du bist ein hilfreicher Assistent, der immer auf Deutsch antwortet und sehr höflich ist."
        user_prompt = "Erkläre mir, was maschinelles Lernen ist."
        
        response = execute_prompt(
            prompt=user_prompt,
            model=OpenAIModel.GPT_4O_MINI,
            system_prompt=system_prompt
        )
        print(f"OpenAI Response: {response}")
        print()
    except Exception as e:
        print(f"OpenAI Error: {e}")
        print()
    
    # Example 2: Using system prompt with Gemini
    print("=== Gemini Example with System Prompt ===")
    try:
        system_prompt = "You are a technical expert who explains complex topics in simple terms."
        user_prompt = "What is the difference between supervised and unsupervised learning?"
        
        response = execute_prompt(
            prompt=user_prompt,
            model=GeminiModel.GEMINI_2_5_FLASH,
            system_prompt=system_prompt
        )
        print(f"Gemini Response: {response}")
        print()
    except Exception as e:
        print(f"Gemini Error: {e}")
        print()
    
    # Example 3: Without system prompt (traditional usage)
    print("=== Example without System Prompt ===")
    try:
        user_prompt = "Explain quantum computing in one sentence."
        
        response = execute_prompt(
            prompt=user_prompt,
            model=OpenAIModel.GPT_4O_MINI
        )
        print(f"Response without system prompt: {response}")
        print()
    except Exception as e:
        print(f"Error: {e}")
        print()


if __name__ == "__main__":
    main()
