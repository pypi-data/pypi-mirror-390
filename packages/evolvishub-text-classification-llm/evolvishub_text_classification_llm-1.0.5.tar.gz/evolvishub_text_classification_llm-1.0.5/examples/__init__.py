"""
Examples package for evolvishub-text-classification-llm.

This package contains comprehensive examples demonstrating how to use
the text classification library with various providers, workflows,
and use cases.
"""

# Example utilities and common configurations
from typing import Dict, Any, List

def get_example_config() -> Dict[str, Any]:
    """Get a basic configuration for examples."""
    return {
        "provider_type": "openai",
        "model": "gpt-3.5-turbo",
        "max_tokens": 100,
        "temperature": 0.1,
        "timeout": 30
    }

def get_example_categories() -> List[str]:
    """Get common categories used in examples."""
    return [
        "customer_satisfaction",
        "customer_complaint", 
        "technical_support",
        "sales_inquiry",
        "billing_question",
        "urgent",
        "normal",
        "low_priority"
    ]

def get_example_texts() -> List[str]:
    """Get sample texts for classification examples."""
    return [
        "I'm extremely happy with your excellent customer service!",
        "This product is terrible and I want a full refund immediately.",
        "How do I configure the API authentication settings?",
        "I'm interested in upgrading to your premium plan.",
        "There's an error in my billing statement from last month.",
        "URGENT: The system is completely down and affecting all users!",
        "Could you please help me understand how this feature works?",
        "The delivery was on time and the product quality is good."
    ]

def get_business_email_examples() -> List[Dict[str, Any]]:
    """Get business email classification examples."""
    return [
        {
            "text": "Thank you for the quick resolution of my technical issue. Your support team was very helpful.",
            "expected_categories": ["customer_satisfaction", "technical_support"],
            "expected_sentiment": "positive"
        },
        {
            "text": "I've been waiting for 3 days for a response to my urgent request. This is unacceptable.",
            "expected_categories": ["customer_complaint", "urgent"],
            "expected_sentiment": "negative"
        },
        {
            "text": "Can you provide pricing information for your enterprise solution?",
            "expected_categories": ["sales_inquiry", "normal"],
            "expected_sentiment": "neutral"
        },
        {
            "text": "The new feature update has significantly improved our workflow efficiency.",
            "expected_categories": ["customer_satisfaction", "normal"],
            "expected_sentiment": "positive"
        }
    ]

def get_multi_provider_example_config() -> Dict[str, Any]:
    """Get configuration for multi-provider examples."""
    return {
        "primary_provider": {
            "provider_type": "openai",
            "model": "gpt-3.5-turbo",
            "max_tokens": 100,
            "temperature": 0.1
        },
        "fallback_provider": {
            "provider_type": "anthropic", 
            "model": "claude-3-haiku-20240307",
            "max_tokens": 100,
            "temperature": 0.1
        },
        "local_provider": {
            "provider_type": "huggingface",
            "model": "microsoft/DialoGPT-medium",
            "device": "auto"
        }
    }

__all__ = [
    "get_example_config",
    "get_example_categories",
    "get_example_texts", 
    "get_business_email_examples",
    "get_multi_provider_example_config"
]
