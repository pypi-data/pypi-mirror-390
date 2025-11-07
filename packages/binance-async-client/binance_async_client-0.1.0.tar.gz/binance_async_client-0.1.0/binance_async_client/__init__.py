"""
币安异步客户端包

一个高性能的异步币安API客户端，支持现货和期货交易，内置智能限流器。
"""

from .client import (
    AsyncBinanceClient,
    AsyncRateLimiter,
    RateLimitConfig,
    get_global_async_client,
    close_global_async_client
)

from .rate_limiter import (
    GlobalRateLimiter,
    get_global_rate_limiter
)

from .futures_client import (
    FuturesAsyncClient
)

__all__ = [
    'AsyncBinanceClient',
    'AsyncRateLimiter',
    'RateLimitConfig',
    'GlobalRateLimiter',
    'FuturesAsyncClient',
    'get_global_async_client',
    'close_global_async_client',
    'get_global_rate_limiter',
]

__version__ = '0.1.0'

