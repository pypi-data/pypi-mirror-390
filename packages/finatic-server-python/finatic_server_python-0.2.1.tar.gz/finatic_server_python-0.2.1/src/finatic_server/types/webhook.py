"""Webhook-related type definitions."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TestWebhookRequest(BaseModel):
    """Request model for testing webhooks."""
    
    event_type: str = Field(..., description="Event type to test (e.g., 'order:filled', 'connection:needs_reauth')")
    sample_data: Optional[Dict[str, Any]] = Field(None, description="Optional custom sample data to include in the webhook")


class TestWebhookResponse(BaseModel):
    """Response model for test webhook requests."""
    
    success: bool = Field(..., description="Whether the test webhook was sent successfully")
    message: str = Field(..., description="Status message")
    sent_to_endpoints: List[str] = Field(..., description="List of endpoint URLs that received the test webhook")
    failed_endpoints: List[str] = Field(..., description="List of endpoint URLs that failed to receive the test webhook")
    webhook_payload: Dict[str, Any] = Field(..., description="The actual webhook payload that was sent")
