"""
异步Binance客户端 - 第二阶段优化核心组件

实现功能：
- 异步HTTP连接池管理
- 智能限流器
- 与现有同步接口兼容
- 错误处理和重试机制
"""

import asyncio
import aiohttp
import time
import logging
import inspect
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import json
import os
import hmac
import hashlib
from urllib.parse import urlencode
# TODO: 提取后需要处理 - 原依赖项目配置系统
# 原代码: from src.core.unified_config import config
# 处理方案1: 通过初始化参数传入 use_proxy: bool
# 处理方案2: 检测环境变量 os.getenv('ENV_MODE') != 'production'
# 临时方案: 使用环境变量检测（保持功能可用）
# config = None  # 将在后续处理中移除

logger = logging.getLogger(__name__)

@dataclass
class RateLimitConfig:
    """限流配置"""
    calls_per_second: float = 15.0  # 🔧 提升：从5.0增加到15.0，提高API处理效率
    burst_size: int = 10
    weight_per_call: int = 1
    max_weight_per_minute: int = 1200

class AsyncRateLimiter:
    """异步限流器 - 令牌桶算法"""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.tokens = config.burst_size
        self.last_update = time.time()
        self.lock = asyncio.Lock()
        
        # 权重限流（币安API权重限制）
        self.weight_tokens = config.max_weight_per_minute
        self.weight_last_update = time.time()
    
    async def acquire(self, weight: int = 1) -> None:
        """获取访问令牌（循环版，防止递归死锁）"""
        while True:
            async with self.lock:
                now = time.time()
                
                # 更新令牌桶
                elapsed = now - self.last_update
                self.tokens = min(
                    self.config.burst_size,
                    self.tokens + elapsed * self.config.calls_per_second
                )
                self.last_update = now
                
                # 更新权重令牌
                weight_elapsed = now - self.weight_last_update
                if weight_elapsed >= 60:  # 每分钟重置权重
                    self.weight_tokens = self.config.max_weight_per_minute
                    self.weight_last_update = now
                
                # 检查是否有足够的令牌和权重
                if self.tokens >= 1 and self.weight_tokens >= weight:
                    self.tokens -= 1
                    self.weight_tokens -= weight
                    return
                
                # 计算等待时间
                if self.tokens < 1:
                    wait_time = (1 - self.tokens) / self.config.calls_per_second
                else:
                    # 权重不足，等到下一分钟
                    wait_time = 60 - (now - self.weight_last_update)
                
                logger.debug(f"限流等待 {wait_time:.2f} 秒，当前令牌: {self.tokens:.2f}, 权重: {self.weight_tokens}")
                await asyncio.sleep(wait_time)
            
    async def safe_acquire(self, weight: int = 1, max_total_wait: float = 30.0):
        """带最大超时保护的acquire，防止死锁"""
        try:
            await asyncio.wait_for(self.acquire(weight), timeout=max_total_wait)
        except asyncio.TimeoutError:
            logger.error(f"限流等待超时（>{max_total_wait}s），可能API权重配置过低或死锁")
            raise

class AsyncBinanceClient:
    """异步Binance客户端"""
    
    def __init__(self, 
                 max_connections: int = 50,
                 max_connections_per_host: int = 20,
                 timeout_total: int = 120,
                 timeout_connect: int = 15,
                 rate_limit_config: Optional[RateLimitConfig] = None,
                 rate_limiter: Optional[Any] = None,
                 api_key: Optional[str] = None,
                 api_secret: Optional[str] = None,
                 default_recv_window: int = 5000,
                 verify_ssl: bool = True):
        
        self.session: Optional[aiohttp.ClientSession] = None
        
        # 优先使用传入的限流器，否则创建本地限流器
        if rate_limiter:
            self.rate_limiter = rate_limiter
            logger.debug("使用外部限流器")
        else:
            self.rate_limiter = AsyncRateLimiter(rate_limit_config or RateLimitConfig())
            logger.debug("使用本地限流器")
        
        # 连接池配置
        self.connector_config = {
            'limit': max_connections,
            'limit_per_host': max_connections_per_host,
            'ttl_dns_cache': 300,  # DNS缓存5分钟
            'use_dns_cache': True,
            'keepalive_timeout': 120,  # 保持连接2分钟
            'enable_cleanup_closed': True,
            'force_close': False,  # 启用连接复用
        }
        
        # 超时配置
        self.timeout_config = aiohttp.ClientTimeout(
            total=timeout_total,
            connect=timeout_connect,
            sock_read=60
        )
        
        # API端点配置
        self.base_urls = [
            'https://api.binance.com',
            'https://api1.binance.com',
            'https://api2.binance.com',
            'https://api3.binance.com'
        ]
        self.current_base_url_index = 0
        
        # 统计信息
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_response_time': 0.0,
            'connection_errors': 0,
            'timeout_errors': 0,
            'rate_limit_errors': 0
        }

        # API凭证
        self.api_key = api_key
        self.api_secret = api_secret
        self.default_recv_window = default_recv_window
        self.verify_ssl = verify_ssl
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()
    
    async def initialize(self):
        """初始化客户端"""
        if self.session is None:
            connector_kwargs = dict(self.connector_config)
            if not self.verify_ssl:
                connector_kwargs['ssl'] = False
                logger.warning("SSL 验证已关闭，此设置仅用于本地调试，生产环境请保持开启。")
            connector = aiohttp.TCPConnector(**connector_kwargs)
            session_kwargs = {
            "connector": connector,
            "timeout": self.timeout_config,
            "headers": {
                'User-Agent': 'binance-async-client/0.1.0',
                'Accept': 'application/json',
                'Accept-Encoding': 'gzip, deflate'
                }
            }
            # TODO: 提取后需要处理 - 原依赖 config.ENV_MODE
            # 原代码: if config.ENV_MODE != 'production':
            # 临时方案: 使用环境变量检测（保持功能可用）
            # 后续处理: 改为通过初始化参数传入 use_proxy: bool
            env_mode = os.getenv('ENV_MODE', 'production')
            if env_mode != 'production':
                session_kwargs["trust_env"] = True
            self.session = aiohttp.ClientSession(**session_kwargs)
            logger.info("异步Binance客户端初始化完成")
    
    async def close(self):
        """关闭客户端"""
        if self.session:
            try:
                # 🔧 修复：添加关闭超时和错误处理
                if not self.session.closed:
                    await asyncio.wait_for(self.session.close(), timeout=5.0)
                logger.info("异步Binance客户端已关闭")
            except asyncio.TimeoutError:
                logger.warning("关闭异步客户端超时")
            except Exception as e:
                logger.error(f"关闭异步客户端失败: {e}")
            finally:
                self.session = None
                
        # 🔧 新增：重置统计信息
        self.reset_stats()
    
    def _get_current_base_url(self) -> str:
        """获取当前API基础URL"""
        return self.base_urls[self.current_base_url_index]
    
    def _rotate_base_url(self):
        """轮换API基础URL"""
        self.current_base_url_index = (self.current_base_url_index + 1) % len(self.base_urls)
        logger.debug(f"切换到API端点: {self._get_current_base_url()}")
    
    def _ensure_credentials(self):
        """确保已配置API凭证"""
        if not self.api_key or not self.api_secret:
            raise RuntimeError("调用该接口需要配置 API Key 和 Secret")

    def _normalize_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """规范化参数，移除 None 并处理布尔值"""
        normalized: Dict[str, Any] = {}
        for key, value in params.items():
            if value is None:
                continue
            if isinstance(value, bool):
                normalized[key] = 'true' if value else 'false'
            else:
                normalized[key] = value
        return normalized

    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """生成HMAC SHA256签名"""
        if not self.api_secret:
            raise RuntimeError("调用该接口需要配置 API Secret")
        query_string = urlencode(params, doseq=True)
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    def _prepare_signed_params(self,
                               params: Optional[Dict[str, Any]] = None,
                               recv_window: Optional[int] = None) -> Dict[str, Any]:
        """准备签名参数，返回新的参数字典"""
        base_params = self._normalize_params(params or {})
        base_params.setdefault('timestamp', int(time.time() * 1000))

        if recv_window is None:
            recv_window = self.default_recv_window
        if recv_window is not None:
            base_params.setdefault('recvWindow', recv_window)

        signature = self._generate_signature(base_params)
        signed_params = dict(base_params)
        signed_params['signature'] = signature
        return signed_params

    async def _make_signed_request(self,
                                   endpoint: str,
                                   params: Optional[Dict[str, Any]] = None,
                                   method: str = 'GET',
                                   weight: int = 1,
                                   max_retries: int = 5,
                                   source: str = 'spot',
                                   recv_window: Optional[int] = None) -> Dict:
        """发起需要签名的请求"""

        self._ensure_credentials()
        method = method.upper()
        normalized_params = self._normalize_params(params or {})
        signed_params = self._prepare_signed_params(normalized_params, recv_window)
        headers = {'X-MBX-APIKEY': self.api_key}

        if method in {'GET', 'DELETE'}:
            request_params = signed_params
            request_data = None
        else:
            request_params = None
            request_data = signed_params

        return await self._make_request(
            endpoint=endpoint,
            params=request_params,
            weight=weight,
            max_retries=max_retries,
            source=source,
            method=method,
            headers=headers,
            data=request_data
        )

    async def _make_request(self, 
                          endpoint: str, 
                          params: Optional[Dict[str, Any]], 
                          weight: int = 1,
                          max_retries: int = 5,
                          source: str = 'spot',
                          method: str = 'GET',
                          headers: Optional[Dict[str, str]] = None,
                          data: Optional[Any] = None) -> Dict:
        """发起HTTP请求"""
        
        if not self.session:
            await self.initialize()
        
        method = method.upper()
        # 限流控制
        # 检查是否是全局限流器（有source参数）
        import inspect
        if hasattr(self.rate_limiter, 'acquire'):
            sig = inspect.signature(self.rate_limiter.acquire)
            if 'source' in sig.parameters:
                # 全局限流器，传递source参数
                await self.rate_limiter.acquire(weight, source)
            elif hasattr(self.rate_limiter, 'safe_acquire'):
                # 本地限流器，使用safe_acquire
                await self.rate_limiter.safe_acquire(weight)
            else:
                # 本地限流器，使用普通acquire
                await self.rate_limiter.acquire(weight)
        
        url = f"{self._get_current_base_url()}{endpoint}"
        
        for attempt in range(max_retries + 1):
            start_time = time.time()
            self.stats['total_requests'] += 1
            
            try:
                request_kwargs: Dict[str, Any] = {
                    'method': method,
                    'url': url,
                    'params': params,
                }
                if headers:
                    request_kwargs['headers'] = headers
                if data is not None:
                    request_kwargs['data'] = data

                async with self.session.request(**request_kwargs) as response:
                    response_time = time.time() - start_time
                    self.stats['total_response_time'] += response_time
                    
                    if response.status == 200:
                        data = await response.json()
                        self.stats['successful_requests'] += 1
                        
                        logger.debug(f"请求成功: {endpoint}, 耗时: {response_time:.2f}s, 数据量: {len(data) if isinstance(data, list) else 1}")
                        return data
                    
                    elif response.status == 429:  # 限流
                        self.stats['rate_limit_errors'] += 1
                        retry_after = int(response.headers.get('Retry-After', 60))
                        logger.warning(f"API限流，等待 {retry_after} 秒后重试")
                        await asyncio.sleep(retry_after)
                        continue
                    
                    elif response.status == 418:  # 币安的"茶壶"状态，表示IP被封
                        self.stats['rate_limit_errors'] += 1
                        error_text = await response.text()
                        
                        # 尝试解析封禁时间
                        import re
                        match = re.search(r'banned until (\d+)', error_text)
                        if match:
                            banned_until = int(match.group(1))
                            wait_seconds = max(0, (banned_until - time.time() * 1000) / 1000)
                            logger.error(f"🚨 IP被封禁(418)，需等待 {wait_seconds:.0f} 秒")
                        else:
                            wait_seconds = 300  # 默认等5分钟
                            logger.error(f"🚨 IP被封禁(418)，等待 {wait_seconds} 秒")
                        
                        # 触发全局限流器的熔断（如果支持）
                        if hasattr(self.rate_limiter, 'trigger_circuit_breaker'):
                            self.rate_limiter.trigger_circuit_breaker(int(wait_seconds))
                        
                        # 不再重试，直接返回None
                        return None  # 重要：不要continue，避免无用重试
                    
                    elif response.status >= 500:  # 服务器错误，尝试其他端点
                        logger.warning(f"服务器错误 {response.status}，尝试其他API端点")
                        self._rotate_base_url()
                        url = f"{self._get_current_base_url()}{endpoint}"
                        continue
                    
                    else:
                        error_text = await response.text()
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status,
                            message=f"HTTP {response.status}: {error_text}"
                        )
            
            except asyncio.TimeoutError:
                self.stats['timeout_errors'] += 1
                logger.warning(f"请求超时 (尝试 {attempt + 1}/{max_retries + 1}): {url}")
                if attempt < max_retries:
                    wait_time = min(2 ** attempt, 10)  # 🔧 修复：限制最大等待时间为10秒
                    await asyncio.sleep(wait_time)
                    continue
                raise
            
            except aiohttp.ClientConnectionError:
                self.stats['connection_errors'] += 1
                logger.warning(f"连接错误 (尝试 {attempt + 1}/{max_retries + 1}): {url}")
                if attempt < max_retries:
                    self._rotate_base_url()
                    url = f"{self._get_current_base_url()}{endpoint}"
                    wait_time = min(2 ** attempt, 8)  # 🔧 修复：限制最大等待时间为8秒
                    await asyncio.sleep(wait_time)
                    continue
                raise
            
            except Exception as e:
                logger.error(f"请求异常 (尝试 {attempt + 1}/{max_retries + 1}): {e}")
                if attempt < max_retries:
                    wait_time = min(2 ** attempt, 5)  # 🔧 修复：限制最大等待时间为5秒
                    await asyncio.sleep(wait_time)
                    continue
                raise
        
        # 所有重试都失败
        self.stats['failed_requests'] += 1
        raise Exception(f"请求失败，已重试 {max_retries} 次: {url}")
    
    async def get_historical_klines_async(self,
                                        symbol: str,
                                        interval: str,
                                        start_time: int,
                                        end_time: int,
                                        limit: int = 1000) -> List[List]:
        """
        异步获取历史K线数据
        
        Args:
            symbol: 交易对符号
            interval: 时间间隔
            start_time: 开始时间戳(毫秒)
            end_time: 结束时间戳(毫秒)
            limit: 限制数量
        
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
        
        # K线数据请求权重为1
        return await self._make_request('/api/v3/klines', params, weight=1)
    
    async def get_exchange_info_async(self) -> Dict:
        """异步获取交易所信息"""
        return await self._make_request('/api/v3/exchangeInfo', {}, weight=10)
    
    async def get_24hr_ticker_async(self, symbol: Optional[str] = None) -> Dict:
        """异步获取24小时价格统计"""
        params = {'symbol': symbol} if symbol else {}
        weight = 1 if symbol else 40
        return await self._make_request('/api/v3/ticker/24hr', params, weight=weight)
    
    def get_performance_stats(self) -> Dict:
        """获取性能统计信息"""
        total_requests = self.stats['total_requests']
        if total_requests == 0:
            return {'status': 'no_requests'}
        
        return {
            'total_requests': total_requests,
            'successful_requests': self.stats['successful_requests'],
            'failed_requests': self.stats['failed_requests'],
            'success_rate': self.stats['successful_requests'] / total_requests,
            'average_response_time': self.stats['total_response_time'] / total_requests,
            'connection_errors': self.stats['connection_errors'],
            'timeout_errors': self.stats['timeout_errors'],
            'rate_limit_errors': self.stats['rate_limit_errors']
        }
    
    def reset_stats(self):
        """重置统计信息"""
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_response_time': 0.0,
            'connection_errors': 0,
            'timeout_errors': 0,
            'rate_limit_errors': 0
        }

# 全局异步客户端实例（可选）
_global_client: Optional[AsyncBinanceClient] = None

async def get_global_async_client() -> AsyncBinanceClient:
    """获取全局异步客户端实例"""
    global _global_client
    if _global_client is None:
        _global_client = AsyncBinanceClient()
        await _global_client.initialize()
    return _global_client

async def close_global_async_client():
    """关闭全局异步客户端"""
    global _global_client
    if _global_client:
        try:
            logger.info("正在关闭全局异步客户端...")
            await _global_client.close()
            logger.info("✅ 全局异步客户端关闭成功")
        except Exception as e:
            logger.error(f"❌ 关闭全局异步客户端失败: {e}")
        finally:
            _global_client = None
    else:
        logger.debug("全局异步客户端已经为空，无需关闭")

# 测试函数
async def test_async_client():
    """测试异步客户端功能"""
    async with AsyncBinanceClient() as client:
        # 测试获取K线数据
        print("测试获取BTCUSDT的1天K线数据...")
        
        # 获取最近2天的数据
        end_time = int(time.time() * 1000)
        start_time = end_time - (2 * 24 * 60 * 60 * 1000)
        
        klines = await client.get_historical_klines_async(
            symbol='BTCUSDT',
            interval='1d',
            start_time=start_time,
            end_time=end_time
        )
        
        print(f"成功获取 {len(klines)} 条K线数据")
        print(f"性能统计: {client.get_performance_stats()}")
        
        return klines

if __name__ == "__main__":
    # 直接运行测试
    asyncio.run(test_async_client()) 