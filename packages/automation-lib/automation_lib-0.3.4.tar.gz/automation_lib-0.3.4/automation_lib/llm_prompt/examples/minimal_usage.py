from automation_lib.llm_prompt.llm_prompt_runner import execute_prompt

# --- Configuration (Optional: Set API key via environment variable) ---
# It's recommended to set your API key as an environment variable, e.g.:
# export OPENAI_API_KEY="your_openai_api_key_here"
# export GEMINI_API_KEY="your_gemini_api_key_here"
# Or, you can pass it directly to the execute_prompt function.

def main():
    print("--- Minimal Usage Example: LLM-Prompt Module ---")

    # Example 1: Basic prompt with default model (from config/default_config.yaml or env)
    print("\nExample 1: Basic prompt with default model")
    try:
        response1 = execute_prompt(
            prompt="What is the capital of Germany?",
            temperature=0.5 # Override temperature for this call
        )
        print(f"Response 1: {response1}")
    except Exception as e:
        print(f"Error in Example 1: {e}")

    # Example 2: Specify a different model and API key (if needed)
    # Make sure you have the API key for the specified model set in your environment
    # or pass it directly.
    print("\nExample 2: Specify a different model (e.g., 'gemini-pro' or 'gpt-3.5-turbo')")
    try:
        # Replace 'gemini-pro' with a model you have access to, e.g., 'gpt-3.5-turbo'
        # If you pass api_key here, it will override the environment variable.
        response2 = execute_prompt(
            prompt="Tell me a short story about a brave knight.",
            model="gpt-4o-mini", # Or "gemini-pro" if you have access
            max_tokens=100,
            # api_key=os.getenv("OPENAI_API_KEY") # Example of passing API key directly
        )
        print(f"Response 2: {response2}")
    except Exception as e:
        print(f"Error in Example 2: {e}")

    # Example 3: Using system prompts to set context
    print("\nExample 3: Using system prompts")
    try:
        response3 = execute_prompt(
            prompt="What should I do if I'm feeling stressed?",
            system_prompt="You are a helpful wellness coach who provides practical, evidence-based advice.",
            model="gpt-4o-mini",
            temperature=0.7
        )
        print(f"Response 3 (with system prompt): {response3}")
    except Exception as e:
        print(f"Error in Example 3: {e}")

    # Example 4: Error handling demonstration (e.g., invalid model)
    print("\nExample 4: Error handling (invalid model)")
    try:
        execute_prompt(
            prompt="This prompt should fail.",
            model="non-existent-model-123"
        )
    except Exception as e:
        print(f"Caught expected error in Example 4: {e}")

if __name__ == "__main__":
    main()
