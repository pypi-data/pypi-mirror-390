import argparse

from automation_lib.llm_prompt.config.llm_prompt_config import load_llm_prompt_config
from automation_lib.llm_prompt.llm_prompt_runner import execute_prompt


def main():
    parser = argparse.ArgumentParser(description="Execute an LLM prompt using LightLLM.")
    parser.add_argument(
        "--prompt",
        type=str,
        required=True,
        help="The text prompt to send to the LLM."
    )
    parser.add_argument(
        "--model",
        type=str,
        help="The name of the LLM model to use (e.g., 'gpt-4', 'gemini-pro'). "
             "If not provided, the default from configuration will be used."
    )
    parser.add_argument(
        "--api_key",
        type=str,
        help="The API key for the LLM service. "
             "If not provided, it will attempt to load from environment variables or configuration."
    )
    parser.add_argument(
        "--temperature",
        type=float,
        help="Controls the randomness of the output. Higher values mean more random."
    )
    parser.add_argument(
        "--max_tokens",
        type=int,
        help="The maximum number of tokens to generate in the completion."
    )
    parser.add_argument(
        "--timeout",
        type=int,
        help="Timeout for the LLM API call in seconds."
    )

    args = parser.parse_args()

    # Load configuration to get defaults if not provided via CLI
    config = load_llm_prompt_config()

    # Determine final values, prioritizing CLI args, then config, then defaults
    final_model = args.model if args.model is not None else config.model_name
    final_api_key = args.api_key if args.api_key is not None else config.api_key
    final_temperature = args.temperature if args.temperature is not None else config.temperature
    final_max_tokens = args.max_tokens if args.max_tokens is not None else config.max_tokens
    final_timeout = args.timeout if args.timeout is not None else config.timeout

    try:
        response_content = execute_prompt(
            prompt=args.prompt,
            model=final_model,
            api_key=final_api_key,
            temperature=final_temperature,
            max_tokens=final_max_tokens,
            timeout=final_timeout
        )
        print("LLM Response:")
        print(response_content)
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)

if __name__ == "__main__":
    main()
