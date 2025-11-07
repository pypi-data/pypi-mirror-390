"""
Finatic Server Python SDK

A Python SDK for integrating with Finatic's server-side trading and portfolio management APIs.
"""

from .core.client import FinaticServerClient
from .core.api_client import ApiClient

# Export all types
from .types import (
    # Common types
    DeviceInfo,
    ApiResponse,
    ApiPaginationInfo,
    PaginationMetadata,
    TradingContext,
    RequestHeaders,
    
    # Authentication types
    UserToken,
    SessionResponse,
    SessionInitResponse,
    OtpRequestResponse,
    OtpVerifyResponse,
    SessionAuthenticateResponse,
    
    # Portfolio types
    Portfolio,
    Holding,
    PerformanceMetrics,
    PortfolioSnapshot,
    
    # Order types
    Order,
    OptionsOrder,
    CryptoOrderOptions,
    OptionsOrderOptions,
    OrderResponse,
    BrokerOrderParams,
    BrokerExtras,
    
    # Broker types
    BrokerAccount,
    BrokerOrder,
    BrokerPosition,
    BrokerInfo,
    BrokerConnection,
    BrokerDataOptions,
    OrdersFilter,
    PositionsFilter,
    AccountsFilter,
    
    # Webhook types
    TestWebhookRequest,
    TestWebhookResponse,
)

# Export all errors
from .utils.errors import (
    FinaticError,
    ApiError,
    AuthenticationError,
    AuthorizationError,
    ValidationError,
    RateLimitError,
    NetworkError,
    TimeoutError,
    OrderError,
    OrderValidationError,
    CompanyAccessError,
    TradingNotEnabledError,
)

__version__ = "0.1.0"
__author__ = "Finatic"
__email__ = "dev@finatic.com"

__all__ = [
    # Main client
    "FinaticServerClient",
    "ApiClient",
    
    # Common types
    "DeviceInfo",
    "ApiResponse",
    "ApiPaginationInfo", 
    "PaginationMetadata",
    "TradingContext",
    "RequestHeaders",
    
    # Authentication types
    "UserToken",
    "SessionResponse",
    "SessionInitResponse",
    "OtpRequestResponse",
    "OtpVerifyResponse",
    "SessionAuthenticateResponse",
    
    # Portfolio types
    "Portfolio",
    "Holding",
    "PerformanceMetrics",
    "PortfolioSnapshot",
    
    # Order types
    "Order",
    "OptionsOrder",
    "CryptoOrderOptions",
    "OptionsOrderOptions",
    "OrderResponse",
    "BrokerOrderParams",
    "BrokerExtras",
    
    # Broker types
    "BrokerAccount",
    "BrokerOrder",
    "BrokerPosition",
    "BrokerInfo",
    "BrokerConnection",
    "BrokerDataOptions",
    "OrdersFilter",
    "PositionsFilter",
    "AccountsFilter",
    
    # Webhook
    "TestWebhookRequest",
    "TestWebhookResponse",
    
    # Errors
    "FinaticError",
    "ApiError",
    "AuthenticationError",
    "AuthorizationError",
    "ValidationError",
    "RateLimitError",
    "NetworkError",
    "TimeoutError",
    "OrderError",
    "OrderValidationError",
    "CompanyAccessError",
    "TradingNotEnabledError",
] 