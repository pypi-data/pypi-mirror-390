#!/usr/bin/env python3
"""
全局API限流器 - 统一管理现货和期货的API调用频率
确保不超过币安API限制
"""

import asyncio
import time
import logging
from typing import Optional
from threading import Lock

logger = logging.getLogger(__name__)


class GlobalRateLimiter:
    """
    全局限流器单例
    统一管理所有币安API请求，避免超限
    """
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化限流器（只执行一次）"""
        if self._initialized:
            return
            
        # 配置参数
        self.calls_per_second = 18.0  # 优化设置：18 QPS（币安限制是20，留2个余量）
        self.burst_size = 30  # 突发容量（提高以支持短时并发）
        self.max_weight_per_minute = 1000  # 币安权重限制（留200余量避免边界情况）
        
        # 令牌桶
        self.tokens = self.burst_size
        self.last_update = time.time()
        self.lock = asyncio.Lock()
        
        # 权重令牌
        self.weight_tokens = self.max_weight_per_minute
        self.weight_last_update = time.time()
        
        # 统计信息
        self.stats = {
            'total_requests': 0,
            'spot_requests': 0,
            'futures_requests': 0,
            'weight_used': 0,
            'rate_limited_count': 0
        }
        
        self._initialized = True
        logger.info(f"✅ 全局限流器初始化: {self.calls_per_second} QPS, "
                   f"权重限制 {self.max_weight_per_minute}/分钟")
    
    async def acquire(self, weight: int = 1, source: str = 'unknown') -> None:
        """
        获取访问令牌
        
        Args:
            weight: API权重
            source: 请求来源（'spot' 或 'futures'）
        """
        while True:
            async with self.lock:
                now = time.time()
                
                # 更新令牌桶
                elapsed = now - self.last_update
                self.tokens = min(
                    self.burst_size,
                    self.tokens + elapsed * self.calls_per_second
                )
                self.last_update = now
                
                # 更新权重令牌（每分钟重置）
                weight_elapsed = now - self.weight_last_update
                if weight_elapsed >= 60:
                    self.weight_tokens = self.max_weight_per_minute
                    self.weight_last_update = now
                    logger.debug(f"🔄 权重令牌重置: {self.max_weight_per_minute}")
                
                # 检查令牌和权重
                if self.tokens >= 1 and self.weight_tokens >= weight:
                    self.tokens -= 1
                    self.weight_tokens -= weight
                    
                    # 更新统计
                    self.stats['total_requests'] += 1
                    self.stats['weight_used'] += weight
                    if source == 'spot':
                        self.stats['spot_requests'] += 1
                    elif source == 'futures':
                        self.stats['futures_requests'] += 1
                    
                    # 日志记录（每100个请求）
                    if self.stats['total_requests'] % 100 == 0:
                        logger.info(f"📊 API使用统计: 总请求={self.stats['total_requests']}, "
                                  f"现货={self.stats['spot_requests']}, "
                                  f"期货={self.stats['futures_requests']}, "
                                  f"剩余权重={self.weight_tokens}/{self.max_weight_per_minute}")
                    
                    return
                
                # 计算等待时间
                if self.tokens < 1:
                    wait_time = (1 - self.tokens) / self.calls_per_second
                else:
                    # 权重不足，等到下一分钟
                    wait_time = 60 - weight_elapsed
                    logger.warning(f"⚠️ API权重不足，需等待 {wait_time:.1f} 秒")
                
                self.stats['rate_limited_count'] += 1
                
            # 在锁外等待
            await asyncio.sleep(wait_time)
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return self.stats.copy()
    
    def reset_stats(self):
        """重置统计信息"""
        self.stats = {
            'total_requests': 0,
            'spot_requests': 0,
            'futures_requests': 0,
            'weight_used': 0,
            'rate_limited_count': 0
        }


# 全局实例
_global_rate_limiter = GlobalRateLimiter()


def get_global_rate_limiter() -> GlobalRateLimiter:
    """获取全局限流器实例"""
    return _global_rate_limiter