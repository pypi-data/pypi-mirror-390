#!/usr/bin/env python3
"""
期货异步客户端 - 复用现货客户端架构，使用全局限流器
"""

import logging
from typing import List, Optional, Dict, Any
# TODO: 提取后需要处理 - 更新导入路径
# 原代码: from src.core.async_binance_client import AsyncBinanceClient
# 原代码: from src.core.global_rate_limiter import get_global_rate_limiter
# 提取后: 使用相对导入
from .client import AsyncBinanceClient
from .rate_limiter import get_global_rate_limiter

logger = logging.getLogger(__name__)


class FuturesAsyncClient(AsyncBinanceClient):
    """
    期货专用异步客户端
    继承现货客户端，但使用期货API端点
    """
    
    def __init__(self, **kwargs):
        """
        初始化期货客户端
        
        自动使用全局限流器，确保与现货模块共享API配额
        """
        # 强制使用全局限流器
        kwargs['rate_limiter'] = get_global_rate_limiter()
        
        super().__init__(**kwargs)
        
        # 覆盖为期货API端点
        self.base_urls = [
            'https://fapi.binance.com',
            'https://fapi1.binance.com',
            'https://fapi2.binance.com',
            'https://fapi3.binance.com'
        ]
        
        logger.info("✅ 期货异步客户端初始化（使用全局限流器）")
    
    async def get_futures_klines_async(self,
                                      symbol: str,
                                      interval: str,
                                      start_time: int,
                                      end_time: int,
                                      limit: int = 1500) -> List[List]:
        """
        获取期货K线数据
        
        Args:
            symbol: 交易对
            interval: 时间间隔
            start_time: 开始时间（毫秒）
            end_time: 结束时间（毫秒）
            limit: 数据条数（期货最大1500）
            
        Returns:
            K线数据列表
        """
        params = {
            'symbol': symbol,
            'interval': interval,
            'startTime': start_time,
            'endTime': end_time,
            'limit': limit
        }
        
        # 使用期货端点，权重为1，标记来源为futures
        return await self._make_request(
            '/fapi/v1/klines', 
            params, 
            weight=1,
            source='futures'  # 用于统计
        )
    
    async def get_futures_exchange_info_async(self) -> dict:
        """获取期货交易所信息"""
        return await self._make_request(
            '/fapi/v1/exchangeInfo',
            {},
            weight=1,
            source='futures'
        )
    
    async def get_futures_24hr_ticker_async(self, symbol: Optional[str] = None) -> dict:
        """获取期货24小时行情"""
        params = {'symbol': symbol} if symbol else {}
        weight = 1 if symbol else 40
        return await self._make_request(
            '/fapi/v1/ticker/24hr',
            params,
            weight=weight,
            source='futures'
        )

    async def get_all_orders_async(self,
                                   symbol: str,
                                   start_time: Optional[int] = None,
                                   end_time: Optional[int] = None,
                                   limit: int = 500,
                                   order_id: Optional[int] = None,
                                   recv_window: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        获取指定交易对的所有订单（包含历史订单）

        Args:
            symbol: 交易对，如 'BTCUSDT'
            start_time: 开始时间戳（毫秒）
            end_time: 结束时间戳（毫秒）
            limit: 返回数量限制，默认500，最大1000
            order_id: 起始订单ID（用于翻页）
            recv_window: 可选的时间窗口（毫秒）

        Returns:
            订单列表
        """

        if limit is not None:
            limit = max(1, min(limit, 1000))

        params = {
            'symbol': symbol,
            'startTime': start_time,
            'endTime': end_time,
            'limit': limit,
            'orderId': order_id,
        }

        return await self._make_signed_request(
            '/fapi/v1/allOrders',
            params=params,
            method='GET',
            weight=5,
            source='futures',
            recv_window=recv_window
        )

    async def get_income_history_async(self,
                                        symbol: Optional[str] = None,
                                        income_type: Optional[str] = None,
                                        start_time: Optional[int] = None,
                                        end_time: Optional[int] = None,
                                        limit: int = 100,
                                        recv_window: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        获取资金流水（如已实现盈亏、资金费用）

        Args:
            symbol: 交易对
            income_type: 收入类型（如 REALIZED_PNL、FUNDING_FEE 等）
            start_time: 开始时间戳（毫秒）
            end_time: 结束时间戳（毫秒）
            limit: 返回数量限制，默认100，最大1000
            recv_window: 可选的时间窗口（毫秒）

        Returns:
            资金流水列表
        """

        if limit is not None:
            limit = max(1, min(limit, 1000))

        params = {
            'symbol': symbol,
            'incomeType': income_type,
            'startTime': start_time,
            'endTime': end_time,
            'limit': limit,
        }

        return await self._make_signed_request(
            '/fapi/v1/income',
            params=params,
            method='GET',
            weight=30,
            source='futures',
            recv_window=recv_window
        )