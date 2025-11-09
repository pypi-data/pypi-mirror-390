"""
Use case examples for evolvishub-text-classification-llm.

This package contains real-world use case examples including
customer support, email classification, content moderation,
sentiment analysis, and business intelligence applications.
"""

# Use case example configurations
from typing import Dict, Any, List

def get_customer_support_use_case() -> Dict[str, Any]:
    """Get customer support classification use case example."""
    return {
        "name": "Customer Support Ticket Classification",
        "description": "Automatically classify customer support tickets by urgency, department, and sentiment",
        "categories": {
            "urgency": ["urgent", "high", "medium", "low"],
            "department": ["technical", "billing", "sales", "general"],
            "sentiment": ["positive", "negative", "neutral"]
        },
        "sample_tickets": [
            {
                "text": "URGENT: Our production server is down and customers can't access the service!",
                "expected": {"urgency": "urgent", "department": "technical", "sentiment": "negative"}
            },
            {
                "text": "Thank you for the excellent support! The issue was resolved quickly.",
                "expected": {"urgency": "low", "department": "general", "sentiment": "positive"}
            },
            {
                "text": "I need help understanding my monthly billing statement.",
                "expected": {"urgency": "medium", "department": "billing", "sentiment": "neutral"}
            }
        ],
        "workflow_config": {
            "providers": ["openai", "anthropic"],
            "fallback_enabled": True,
            "confidence_threshold": 0.7
        }
    }

def get_email_classification_use_case() -> Dict[str, Any]:
    """Get business email classification use case example."""
    return {
        "name": "Business Email Classification",
        "description": "Classify incoming business emails for routing and prioritization",
        "categories": {
            "type": ["inquiry", "complaint", "compliment", "request", "notification"],
            "priority": ["urgent", "high", "normal", "low"],
            "department": ["sales", "support", "hr", "finance", "legal"]
        },
        "sample_emails": [
            {
                "subject": "Partnership Opportunity - Fortune 500 Company",
                "text": "We're interested in exploring a strategic partnership with your company...",
                "expected": {"type": "inquiry", "priority": "high", "department": "sales"}
            },
            {
                "subject": "Invoice Payment Issue",
                "text": "There seems to be an error in invoice #12345. The amount charged doesn't match...",
                "expected": {"type": "complaint", "priority": "normal", "department": "finance"}
            }
        ],
        "processing_rules": {
            "auto_route": True,
            "escalation_keywords": ["urgent", "asap", "immediately", "critical"],
            "vip_senders": ["@enterprise-client.com", "@major-partner.com"]
        }
    }

def get_content_moderation_use_case() -> Dict[str, Any]:
    """Get content moderation use case example."""
    return {
        "name": "Social Media Content Moderation",
        "description": "Automatically moderate user-generated content for policy violations",
        "categories": {
            "safety": ["safe", "questionable", "unsafe"],
            "toxicity": ["non_toxic", "mildly_toxic", "toxic", "very_toxic"],
            "spam": ["not_spam", "likely_spam", "spam"]
        },
        "sample_content": [
            {
                "text": "Great product! Highly recommend to everyone.",
                "expected": {"safety": "safe", "toxicity": "non_toxic", "spam": "not_spam"}
            },
            {
                "text": "This is terrible! I hate this stupid product and everyone who made it!",
                "expected": {"safety": "questionable", "toxicity": "mildly_toxic", "spam": "not_spam"}
            }
        ],
        "moderation_rules": {
            "auto_approve_threshold": 0.9,
            "auto_reject_threshold": 0.3,
            "human_review_range": [0.3, 0.9]
        }
    }

def get_sentiment_analysis_use_case() -> Dict[str, Any]:
    """Get sentiment analysis use case example."""
    return {
        "name": "Product Review Sentiment Analysis",
        "description": "Analyze customer product reviews for sentiment and key insights",
        "categories": {
            "sentiment": ["very_positive", "positive", "neutral", "negative", "very_negative"],
            "aspect": ["quality", "price", "service", "delivery", "features"],
            "recommendation": ["highly_recommend", "recommend", "neutral", "not_recommend"]
        },
        "sample_reviews": [
            {
                "text": "Amazing product quality and fast delivery! Worth every penny.",
                "expected": {"sentiment": "very_positive", "aspect": "quality", "recommendation": "highly_recommend"}
            },
            {
                "text": "The product is okay but overpriced for what you get.",
                "expected": {"sentiment": "neutral", "aspect": "price", "recommendation": "neutral"}
            }
        ],
        "analytics_features": {
            "trend_analysis": True,
            "competitor_comparison": True,
            "aspect_based_insights": True
        }
    }

def get_business_intelligence_use_case() -> Dict[str, Any]:
    """Get business intelligence use case example."""
    return {
        "name": "Market Research Text Analysis",
        "description": "Analyze market research data and customer feedback for business insights",
        "categories": {
            "market_trend": ["growing", "stable", "declining"],
            "customer_need": ["feature_request", "price_concern", "quality_issue", "service_improvement"],
            "competitive_position": ["advantage", "parity", "disadvantage"]
        },
        "sample_feedback": [
            {
                "text": "Customers are increasingly asking for mobile app features and cloud integration.",
                "expected": {"market_trend": "growing", "customer_need": "feature_request", "competitive_position": "advantage"}
            }
        ],
        "reporting_features": {
            "automated_insights": True,
            "trend_visualization": True,
            "executive_summary": True
        }
    }

__all__ = [
    "get_customer_support_use_case",
    "get_email_classification_use_case",
    "get_content_moderation_use_case",
    "get_sentiment_analysis_use_case",
    "get_business_intelligence_use_case"
]
