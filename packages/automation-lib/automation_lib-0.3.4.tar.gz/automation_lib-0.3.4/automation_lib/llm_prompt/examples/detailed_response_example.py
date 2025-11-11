"""
Detailed Response Example

This example demonstrates how to use the execute_prompt_detailed function
to get comprehensive metadata about LLM responses including token usage,
response times, and rate limit information.
"""

from automation_lib.llm_prompt import GeminiModel, OpenAIModel, execute_prompt_detailed
from automation_lib.llm_prompt.config.llm_prompt_config import LLMPromptConfig


def main():
    """Demonstrate detailed LLM response functionality."""
    
    # Example prompt
    prompt = "Explain the concept of machine learning in 2-3 sentences."
    system_prompt = "You are a helpful AI assistant that provides clear and concise explanations."
    
    print("=== Detailed LLM Response Example ===\n")
    
    # Example 1: Using OpenAI with detailed response
    print("1. OpenAI GPT-4o-mini with detailed response:")
    print("-" * 50)
    
    try:
        # Configure for OpenAI
        config = LLMPromptConfig.default()
        
        # Execute prompt with detailed response
        response = execute_prompt_detailed(
            prompt=prompt,
            model=OpenAIModel.GPT_4O_MINI,
            system_prompt=system_prompt,
            config=config,
            temperature=0.7
        )
        
        # Display detailed information
        print(f"Content: {response.content}")
        print(f"Model: {response.model}")
        print(f"Provider: {response.provider}")
        print(f"Response Time: {response.response_time_ms}ms")
        print(f"Finish Reason: {response.finish_reason}")
        print(f"Request ID: {response.request_id}")
        print(f"Created At: {response.created_at}")
        
        if response.token_usage:
            print("Token Usage:")
            print(f"  - Prompt Tokens: {response.token_usage.prompt_tokens}")
            print(f"  - Completion Tokens: {response.token_usage.completion_tokens}")
            print(f"  - Total Tokens: {response.token_usage.total_tokens}")
        
        if response.rate_limit_info:
            print("Rate Limit Info:")
            print(f"  - Requests Remaining: {response.rate_limit_info.requests_remaining}")
            print(f"  - Tokens Remaining: {response.rate_limit_info.tokens_remaining}")
            print(f"  - Requests Reset Time: {response.rate_limit_info.requests_reset_time}")
            print(f"  - Tokens Reset Time: {response.rate_limit_info.tokens_reset_time}")
        else:
            print("Rate Limit Info: Not available")
            
    except Exception as e:
        print(f"Error with OpenAI: {e}")
    
    print("\n" + "="*60 + "\n")
    
    # Example 2: Using Gemini with detailed response
    print("2. Google Gemini with detailed response:")
    print("-" * 50)
    
    try:
        # Execute prompt with Gemini
        response = execute_prompt_detailed(
            prompt=prompt,
            model=GeminiModel.GEMINI_2_5_FLASH,
            system_prompt=system_prompt,
            temperature=0.7
        )
        
        # Display detailed information
        print(f"Content: {response.content}")
        print(f"Model: {response.model}")
        print(f"Provider: {response.provider}")
        print(f"Response Time: {response.response_time_ms}ms")
        print(f"Finish Reason: {response.finish_reason}")
        print(f"Created At: {response.created_at}")
        
        if response.token_usage:
            print("Token Usage:")
            print(f"  - Prompt Tokens: {response.token_usage.prompt_tokens}")
            print(f"  - Completion Tokens: {response.token_usage.completion_tokens}")
            print(f"  - Total Tokens: {response.token_usage.total_tokens}")
        else:
            print("Token Usage: Not available")
        
        if response.rate_limit_info:
            print("Rate Limit Info:")
            print(f"  - Requests Remaining: {response.rate_limit_info.requests_remaining}")
            print(f"  - Tokens Remaining: {response.rate_limit_info.tokens_remaining}")
        else:
            print("Rate Limit Info: Not available")
            
    except Exception as e:
        print(f"Error with Gemini: {e}")
    
    print("\n" + "="*60 + "\n")
    
    # Example 3: Comparing response times and token usage
    print("3. Performance Comparison:")
    print("-" * 50)
    
    models_to_test = [
        (OpenAIModel.GPT_4O_MINI, "OpenAI GPT-4o-mini"),
        (GeminiModel.GEMINI_2_5_FLASH, "Gemini 1.5 Flash")
    ]
    
    simple_prompt = "What is Python?"
    
    for model, model_name in models_to_test:
        try:
            response = execute_prompt_detailed(
                prompt=simple_prompt,
                model=model,
                temperature=0.5
            )
            
            print(f"{model_name}:")
            print(f"  Response Time: {response.response_time_ms}ms")
            if response.token_usage:
                print(f"  Total Tokens: {response.token_usage.total_tokens}")
            print(f"  Content Length: {len(response.content)} characters")
            print()
            
        except Exception as e:
            print(f"{model_name}: Error - {e}")
            print()


if __name__ == "__main__":
    main()
