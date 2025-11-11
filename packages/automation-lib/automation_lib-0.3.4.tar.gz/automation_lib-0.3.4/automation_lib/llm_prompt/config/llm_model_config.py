"""
Configuration for commonly used LLM models, including their names and properties.
"""

LLM_MODELS = {
    "openai": {
        "o3": {
            "name": "o3",
            "description": "OpenAI's most intelligent reasoning model, designed for complex problem-solving tasks in research, strategy, coding, math, and science.",
            "properties": "Advanced reasoning, complex problem-solving, research-grade performance."
        },
        "o3-pro": {
            "name": "o3-pro",
            "description": "Enhanced version of o3 designed to think longer and provide the most reliable responses for the most challenging tasks.",
            "properties": "Extended reasoning time, highest reliability, premium performance."
        },
        "o4-mini": {
            "name": "o4-mini",
            "description": "A smaller, faster reasoning model that balances performance with efficiency for everyday problem-solving tasks.",
            "properties": "Fast reasoning, cost-effective, good for routine complex tasks."
        },
        "gpt-4.1": {
            "name": "gpt-4.1",
            "description": "Specialized model that excels at coding tasks with precise instruction following and web development capabilities.",
            "properties": "Excellent for coding, precise instruction following, web development."
        },
        "gpt-4o": {
            "name": "gpt-4o",
            "description": "OpenAI's multimodal flagship model with vision, audio, and text capabilities. Fast and cost-effective.",
            "properties": "Multimodal (text, image, audio), fast, cost-effective, high performance."
        },
        "gpt-4o-mini": {
            "name": "gpt-4o-mini",
            "description": "A smaller, faster, and more affordable version of GPT-4o, optimized for simpler tasks.",
            "properties": "Fast, very cost-effective, good for simpler tasks."
        }
    },
    "gemini": {
        "gemini-2.5-pro": {
            "name": "gemini-2.5-pro",
            "description": "Google's most advanced Gemini model with built-in 'thinking' capabilities for complex reasoning and problem-solving.",
            "properties": "Most advanced, strong reasoning, coding capabilities, 'thinking' feature."
        },
        "gemini-2.5-flash": {
            "name": "gemini-2.5-flash",
            "description": "Google's best model in terms of price-performance, offering well-rounded capabilities with improved speed.",
            "properties": "Best price-performance ratio, well-rounded, fast."
        },
        "gemini-2.5-flash-lite": {
            "name": "gemini-2.5-flash-lite",
            "description": "Google's most cost-efficient and fastest 2.5 model, with higher quality than 2.0 Flash-Lite on coding tasks.",
            "properties": "Most cost-efficient, fastest, good coding performance."
        },
        "gemini-2.0-flash": {
            "name": "gemini-2.0-flash",
            "description": "Production-ready Gemini 2.0 model designed for the agentic era, now generally available.",
            "properties": "Production-ready, agentic capabilities, generally available."
        },
        "gemini-2.0-flash-lite": {
            "name": "gemini-2.0-flash-lite",
            "description": "Ultra-fast and cost-efficient Gemini 2.0 model with high rate limits, ideal for high-volume applications.",
            "properties": "Ultra-fast, very cost-efficient, high rate limits (30 RPM free tier)."
        },
        "gemini-2.0-pro": {
            "name": "gemini-2.0-pro",
            "description": "Experimental version of Gemini 2.0 Pro, Google's best model for coding performance in the 2.0 series.",
            "properties": "Experimental, best coding performance in 2.0 series, advanced capabilities."
        }
    }
}
