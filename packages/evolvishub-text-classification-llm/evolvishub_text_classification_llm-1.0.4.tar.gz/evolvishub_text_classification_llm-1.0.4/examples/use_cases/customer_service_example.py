#!/usr/bin/env python3
"""
Customer Service Email Classification Example

This example demonstrates a complete customer service email classification system
that can be used by businesses to automatically categorize and route customer emails.

Features demonstrated:
- Multi-category email classification
- Urgency detection and priority routing
- Department assignment
- Customer satisfaction analysis
- Automated response suggestions
- Batch processing for email queues
- Integration with ticketing systems
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from evolvishub_text_classification_llm import (
    ClassificationEngine,
    BatchProcessor,
    WorkflowConfig,
    ProviderConfig,
    ProviderType
)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CustomerEmail:
    """Represents a customer email."""
    id: str
    subject: str
    content: str
    sender_email: str
    received_at: datetime
    customer_tier: str = "standard"  # standard, premium, enterprise
    previous_interactions: int = 0


@dataclass
class EmailClassificationResult:
    """Enhanced classification result for customer service."""
    email_id: str
    primary_category: str
    confidence: float
    urgency_level: str
    suggested_department: str
    customer_satisfaction_score: float
    requires_immediate_attention: bool
    suggested_response_template: str
    estimated_resolution_time: str
    processing_time_ms: float


class CustomerServiceClassifier:
    """
    Customer service email classification system.
    
    This class provides a complete solution for classifying customer service emails
    with business-specific logic and routing capabilities.
    """
    
    def __init__(self, provider_type: str = "openai", model: str = "gpt-4"):
        """Initialize the customer service classifier."""
        self.provider_type = provider_type
        self.model = model
        self.engine = None
        self.batch_processor = None
        
        # Business categories for customer service
        self.categories = [
            "complaint_billing",
            "complaint_service_quality", 
            "complaint_technical_issue",
            "complaint_delivery",
            "inquiry_product_information",
            "inquiry_account_status",
            "inquiry_billing_question",
            "inquiry_technical_support",
            "request_refund",
            "request_exchange",
            "request_account_change",
            "request_feature",
            "compliment_service",
            "compliment_product",
            "urgent_account_security",
            "urgent_service_outage",
            "routine_communication"
        ]
        
        # Department routing rules
        self.department_routing = {
            "complaint_billing": "billing",
            "complaint_service_quality": "customer_success",
            "complaint_technical_issue": "technical_support",
            "complaint_delivery": "logistics",
            "inquiry_product_information": "sales",
            "inquiry_account_status": "customer_success",
            "inquiry_billing_question": "billing",
            "inquiry_technical_support": "technical_support",
            "request_refund": "billing",
            "request_exchange": "customer_success",
            "request_account_change": "customer_success",
            "request_feature": "product_management",
            "compliment_service": "customer_success",
            "compliment_product": "product_management",
            "urgent_account_security": "security",
            "urgent_service_outage": "technical_support",
            "routine_communication": "customer_success"
        }
        
        # Response templates
        self.response_templates = {
            "complaint_billing": "billing_complaint_response",
            "complaint_service_quality": "service_quality_response",
            "complaint_technical_issue": "technical_issue_response",
            "inquiry_product_information": "product_info_response",
            "request_refund": "refund_process_response",
            "compliment_service": "thank_you_response",
            "urgent_account_security": "security_urgent_response"
        }
    
    async def initialize(self):
        """Initialize the classification system."""
        try:
            # Create comprehensive system prompt
            system_prompt = """You are an expert customer service email classifier with deep understanding of business operations and customer psychology.

Your expertise includes:
- Customer service communication patterns and escalation procedures
- Business email categorization and priority assessment
- Customer satisfaction analysis and sentiment detection
- Urgency detection and department routing optimization
- Technical support issue identification and complexity assessment

You analyze emails considering:
- Explicit customer requests and complaints
- Emotional tone and satisfaction indicators
- Technical complexity and urgency signals
- Business impact and customer tier implications
- Historical interaction patterns and context

Always provide accurate, actionable classifications that enable excellent customer service delivery."""

            # Create detailed user prompt template
            user_prompt_template = """Analyze this customer service email and provide comprehensive classification:

EMAIL DETAILS:
Subject: {subject}
Content: {content}
Customer Tier: {customer_tier}
Previous Interactions: {previous_interactions}

Classify into the most appropriate category from:
{categories}

Provide a JSON response with:
{{
  "primary_category": "most_relevant_category",
  "confidence": 0.95,
  "urgency_level": "low|medium|high|critical",
  "customer_satisfaction_score": 0.85,
  "requires_immediate_attention": true|false,
  "suggested_department": "department_name",
  "estimated_resolution_time": "1 hour|4 hours|1 day|3 days",
  "key_issues": ["issue1", "issue2"],
  "customer_emotion": "frustrated|satisfied|neutral|angry|pleased",
  "technical_complexity": "low|medium|high",
  "business_impact": "low|medium|high",
  "reasoning": "Detailed explanation of classification decision"
}}"""

            # Create provider configuration
            provider_config = ProviderConfig(
                provider_type=ProviderType(self.provider_type),
                model=self.model,
                api_key="your-api-key",  # Replace with actual key
                temperature=0.1,
                max_tokens=800,
                timeout_seconds=30
            )
            
            # Create workflow configuration
            workflow_config = WorkflowConfig(
                name="customer_service_classification",
                primary_provider=provider_config,
                categories=self.categories,
                system_prompt=system_prompt,
                user_prompt_template=user_prompt_template,
                min_confidence_threshold=0.7
            )
            
            # Initialize classification engine
            self.engine = ClassificationEngine(config=workflow_config)
            await self.engine.initialize()
            
            # Initialize batch processor
            self.batch_processor = BatchProcessor(
                engine=self.engine,
                max_concurrent=5,
                batch_size=50
            )
            
            logger.info("Customer service classifier initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize classifier: {e}")
            raise
    
    async def classify_email(self, email: CustomerEmail) -> EmailClassificationResult:
        """Classify a single customer email."""
        try:
            # Prepare email content for classification
            email_text = f"Subject: {email.subject}\n\nContent: {email.content}"
            
            # Create metadata with business context
            metadata = {
                "customer_tier": email.customer_tier,
                "previous_interactions": email.previous_interactions,
                "subject": email.subject
            }
            
            # Perform classification
            result = await self.engine.classify(email_text, metadata)
            
            # Extract business-specific information
            classification_data = self._extract_business_data(result)
            
            # Create enhanced result
            enhanced_result = EmailClassificationResult(
                email_id=email.id,
                primary_category=result.primary_category,
                confidence=result.confidence,
                urgency_level=classification_data.get("urgency_level", "medium"),
                suggested_department=self._get_department(result.primary_category),
                customer_satisfaction_score=classification_data.get("customer_satisfaction_score", 0.5),
                requires_immediate_attention=classification_data.get("requires_immediate_attention", False),
                suggested_response_template=self._get_response_template(result.primary_category),
                estimated_resolution_time=classification_data.get("estimated_resolution_time", "1 day"),
                processing_time_ms=result.processing_time_ms
            )
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Failed to classify email {email.id}: {e}")
            raise
    
    async def classify_email_batch(self, emails: List[CustomerEmail]) -> List[EmailClassificationResult]:
        """Classify a batch of customer emails."""
        try:
            # Prepare texts for batch processing
            texts = []
            metadata_list = []
            
            for email in emails:
                email_text = f"Subject: {email.subject}\n\nContent: {email.content}"
                texts.append(email_text)
                
                metadata = {
                    "email_id": email.id,
                    "customer_tier": email.customer_tier,
                    "previous_interactions": email.previous_interactions
                }
                metadata_list.append(metadata)
            
            # Process batch
            results = await self.batch_processor.process_batch(texts, metadata_list)
            
            # Convert to enhanced results
            enhanced_results = []
            for i, result in enumerate(results):
                email = emails[i]
                classification_data = self._extract_business_data(result)
                
                enhanced_result = EmailClassificationResult(
                    email_id=email.id,
                    primary_category=result.primary_category,
                    confidence=result.confidence,
                    urgency_level=classification_data.get("urgency_level", "medium"),
                    suggested_department=self._get_department(result.primary_category),
                    customer_satisfaction_score=classification_data.get("customer_satisfaction_score", 0.5),
                    requires_immediate_attention=classification_data.get("requires_immediate_attention", False),
                    suggested_response_template=self._get_response_template(result.primary_category),
                    estimated_resolution_time=classification_data.get("estimated_resolution_time", "1 day"),
                    processing_time_ms=result.processing_time_ms
                )
                enhanced_results.append(enhanced_result)
            
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Failed to classify email batch: {e}")
            raise
    
    def _extract_business_data(self, result) -> Dict[str, Any]:
        """Extract business-specific data from classification result."""
        # Real business logic based on actual classification results
        primary_category = result.primary_category.lower()
        confidence = result.confidence
        categories = [cat.lower() for cat in result.categories]

        # Determine urgency based on actual classification
        urgency_level = "low"
        if any(keyword in primary_category for keyword in ["urgent", "emergency", "critical"]):
            urgency_level = "high"
        elif any(keyword in primary_category for keyword in ["complaint", "issue", "problem"]):
            urgency_level = "medium"
        elif confidence < 0.5:
            urgency_level = "medium"  # Low confidence requires review

        # Calculate customer satisfaction score based on sentiment
        satisfaction_score = 0.5  # neutral default
        if any(keyword in primary_category for keyword in ["positive", "compliment", "praise"]):
            satisfaction_score = 0.9
        elif any(keyword in primary_category for keyword in ["negative", "complaint", "angry"]):
            satisfaction_score = 0.2
        elif any(keyword in primary_category for keyword in ["neutral", "inquiry", "question"]):
            satisfaction_score = 0.7

        # Determine if immediate attention is required
        requires_immediate_attention = (
            urgency_level == "high" or
            confidence < 0.3 or  # Very low confidence
            any(keyword in primary_category for keyword in ["refund", "cancel", "legal"])
        )

        # Estimate resolution time based on category and urgency
        if urgency_level == "high":
            resolution_time = "1 hour"
        elif urgency_level == "medium":
            resolution_time = "4 hours"
        else:
            resolution_time = "1 day"

        return {
            "urgency_level": urgency_level,
            "customer_satisfaction_score": satisfaction_score,
            "requires_immediate_attention": requires_immediate_attention,
            "estimated_resolution_time": resolution_time,
            "confidence_level": "high" if confidence > 0.8 else "medium" if confidence > 0.5 else "low",
            "routing_department": self._determine_routing_department(primary_category),
            "priority_score": self._calculate_priority_score(urgency_level, satisfaction_score, confidence)
        }

    def _determine_routing_department(self, category: str) -> str:
        """Determine which department should handle this request."""
        if any(keyword in category for keyword in ["billing", "payment", "refund", "charge"]):
            return "billing"
        elif any(keyword in category for keyword in ["technical", "bug", "error", "not working"]):
            return "technical_support"
        elif any(keyword in category for keyword in ["sales", "purchase", "buy", "pricing"]):
            return "sales"
        elif any(keyword in category for keyword in ["complaint", "angry", "dissatisfied"]):
            return "customer_relations"
        else:
            return "general_support"

    def _calculate_priority_score(self, urgency: str, satisfaction: float, confidence: float) -> int:
        """Calculate priority score from 1-10 (10 being highest priority)."""
        score = 5  # base score

        # Adjust for urgency
        if urgency == "high":
            score += 3
        elif urgency == "medium":
            score += 1

        # Adjust for customer satisfaction (lower satisfaction = higher priority)
        if satisfaction < 0.3:
            score += 2
        elif satisfaction < 0.6:
            score += 1

        # Adjust for confidence (lower confidence = higher priority for review)
        if confidence < 0.5:
            score += 1

        return min(10, max(1, score))
    
    def _get_department(self, category: str) -> str:
        """Get suggested department for a category."""
        return self.department_routing.get(category, "customer_success")
    
    def _get_response_template(self, category: str) -> str:
        """Get suggested response template for a category."""
        return self.response_templates.get(category, "standard_response")
    
    async def get_classification_stats(self) -> Dict[str, Any]:
        """Get classification statistics."""
        if self.engine:
            return await self.engine.get_usage_stats()
        return {}
    
    async def cleanup(self):
        """Cleanup resources."""
        if self.engine:
            await self.engine.cleanup()


async def demo_single_email_classification():
    """Demonstrate single email classification."""
    print("\n📧 Single Email Classification Demo")
    print("=" * 50)
    
    # Create sample customer emails
    sample_emails = [
        CustomerEmail(
            id="email_001",
            subject="URGENT: Account compromised - need immediate help!",
            content="Hi, I just noticed unauthorized transactions on my account. Someone has been using my credit card and I need this resolved immediately. This is a security emergency!",
            sender_email="customer@example.com",
            received_at=datetime.now(),
            customer_tier="premium",
            previous_interactions=2
        ),
        CustomerEmail(
            id="email_002", 
            subject="Question about premium features",
            content="Hello, I'm interested in upgrading to your premium plan. Could you please send me more information about the additional features and pricing? Thank you!",
            sender_email="prospect@example.com",
            received_at=datetime.now(),
            customer_tier="standard",
            previous_interactions=0
        ),
        CustomerEmail(
            id="email_003",
            subject="Billing error on my invoice",
            content="I received my monthly invoice and there seems to be an error. I was charged twice for the same service. Can someone please review my account and correct this?",
            sender_email="billing@customer.com",
            received_at=datetime.now(),
            customer_tier="enterprise",
            previous_interactions=5
        )
    ]
    
    # Initialize classifier
    classifier = CustomerServiceClassifier(provider_type="openai", model="gpt-4")
    await classifier.initialize()
    
    print("Classifying individual emails...")
    
    for email in sample_emails:
        result = await classifier.classify_email(email)
        
        print(f"\n📨 Email ID: {result.email_id}")
        print(f"   Subject: {email.subject}")
        print(f"   Category: {result.primary_category}")
        print(f"   Confidence: {result.confidence:.3f}")
        print(f"   Urgency: {result.urgency_level}")
        print(f"   Department: {result.suggested_department}")
        print(f"   Satisfaction Score: {result.customer_satisfaction_score:.2f}")
        print(f"   Immediate Attention: {result.requires_immediate_attention}")
        print(f"   Response Template: {result.suggested_response_template}")
        print(f"   Est. Resolution: {result.estimated_resolution_time}")
        print(f"   Processing Time: {result.processing_time_ms:.1f}ms")
    
    await classifier.cleanup()


async def demo_batch_email_processing():
    """Demonstrate batch email processing."""
    print("\n📬 Batch Email Processing Demo")
    print("=" * 50)
    
    # Create a larger batch of emails
    batch_emails = [
        CustomerEmail(
            id=f"batch_email_{i:03d}",
            subject=subject,
            content=content,
            sender_email=f"customer{i}@example.com",
            received_at=datetime.now(),
            customer_tier=tier,
            previous_interactions=interactions
        )
        for i, (subject, content, tier, interactions) in enumerate([
            ("Product not working", "The product stopped working after 2 days", "standard", 1),
            ("Love your service!", "Just wanted to say your customer service is amazing", "premium", 3),
            ("Refund request", "I need to return this product and get a refund", "standard", 0),
            ("Technical issue", "The app crashes when I try to upload files", "enterprise", 2),
            ("Billing question", "Can you explain this charge on my account?", "premium", 1),
            ("Feature request", "Would love to see dark mode in the app", "standard", 4),
            ("Account locked", "I can't log into my account, please help", "enterprise", 0),
            ("Thank you note", "Excellent support from your team yesterday", "premium", 2),
            ("Delivery problem", "My order hasn't arrived yet", "standard", 1),
            ("Upgrade inquiry", "Interested in enterprise features", "standard", 0)
        ], 1)
    ]
    
    # Initialize classifier
    classifier = CustomerServiceClassifier(provider_type="openai", model="gpt-3.5-turbo")
    await classifier.initialize()
    
    print(f"Processing batch of {len(batch_emails)} emails...")
    
    import time
    start_time = time.time()
    
    results = await classifier.classify_email_batch(batch_emails)
    
    end_time = time.time()
    total_time = (end_time - start_time) * 1000
    
    # Analyze results
    category_counts = {}
    department_counts = {}
    urgent_count = 0
    high_satisfaction = 0
    
    for result in results:
        # Count categories
        category_counts[result.primary_category] = category_counts.get(result.primary_category, 0) + 1
        
        # Count departments
        department_counts[result.suggested_department] = department_counts.get(result.suggested_department, 0) + 1
        
        # Count urgent emails
        if result.requires_immediate_attention:
            urgent_count += 1
        
        # Count high satisfaction
        if result.customer_satisfaction_score > 0.7:
            high_satisfaction += 1
    
    print(f"\n📊 Batch Processing Results:")
    print(f"   Total emails processed: {len(results)}")
    print(f"   Total processing time: {total_time:.1f}ms")
    print(f"   Average per email: {total_time/len(results):.1f}ms")
    print(f"   Throughput: {len(results)/(total_time/1000):.1f} emails/second")
    
    print(f"\n📈 Classification Summary:")
    print(f"   Urgent emails: {urgent_count}")
    print(f"   High satisfaction: {high_satisfaction}")
    print(f"   Average confidence: {sum(r.confidence for r in results)/len(results):.3f}")
    
    print(f"\n🏷️ Category Distribution:")
    for category, count in sorted(category_counts.items()):
        print(f"   {category}: {count}")
    
    print(f"\n🏢 Department Routing:")
    for department, count in sorted(department_counts.items()):
        print(f"   {department}: {count}")
    
    await classifier.cleanup()


async def demo_real_time_monitoring():
    """Demonstrate real-time email monitoring."""
    print("\n📊 Real-Time Email Monitoring Demo")
    print("=" * 50)
    
    classifier = CustomerServiceClassifier()
    await classifier.initialize()
    
    # Simulate real-time email processing
    print("Simulating real-time email processing...")
    
    # Create a stream of emails
    email_stream = [
        ("CRITICAL: System down!", "Our entire system is down and customers can't access their accounts!", "critical"),
        ("Thank you!", "Great service as always, keep up the good work!", "low"),
        ("Billing issue", "There's an error on my invoice that needs correction", "medium"),
        ("Feature request", "Would love to see integration with Slack", "low"),
        ("Account problem", "Can't reset my password, need help", "medium")
    ]
    
    urgent_queue = []
    normal_queue = []
    
    for i, (subject, content, priority) in enumerate(email_stream):
        email = CustomerEmail(
            id=f"stream_{i}",
            subject=subject,
            content=content,
            sender_email=f"customer{i}@example.com",
            received_at=datetime.now(),
            customer_tier="standard"
        )
        
        result = await classifier.classify_email(email)
        
        print(f"\n📨 Processing: {subject}")
        print(f"   Category: {result.primary_category}")
        print(f"   Urgency: {result.urgency_level}")
        print(f"   Department: {result.suggested_department}")
        
        # Route to appropriate queue
        if result.requires_immediate_attention:
            urgent_queue.append(result)
            print(f"   ⚠️ ROUTED TO URGENT QUEUE")
        else:
            normal_queue.append(result)
            print(f"   ✅ Routed to normal queue")
    
    print(f"\n📋 Queue Status:")
    print(f"   Urgent queue: {len(urgent_queue)} emails")
    print(f"   Normal queue: {len(normal_queue)} emails")
    
    # Show urgent emails
    if urgent_queue:
        print(f"\n🚨 Urgent Emails Requiring Immediate Attention:")
        for result in urgent_queue:
            print(f"   • {result.email_id}: {result.primary_category} -> {result.suggested_department}")
    
    await classifier.cleanup()


async def main():
    """Run all customer service examples."""
    print("📧 Customer Service Email Classification Examples")
    print("=" * 60)
    print("Demonstrating enterprise-grade email classification system")
    print("=" * 60)
    
    examples = [
        demo_single_email_classification,
        demo_batch_email_processing,
        demo_real_time_monitoring
    ]
    
    for example_func in examples:
        try:
            await example_func()
        except Exception as e:
            print(f"❌ Example {example_func.__name__} failed: {e}")
        
        print("\n" + "="*60)
    
    print("✅ All customer service examples completed!")
    print("\n💡 Business Benefits:")
    print("• Automatic email categorization and routing")
    print("• Priority detection for urgent issues")
    print("• Department assignment optimization")
    print("• Customer satisfaction monitoring")
    print("• Response template suggestions")
    print("• Scalable batch processing")
    print("• Real-time monitoring capabilities")


if __name__ == "__main__":
    asyncio.run(main())
