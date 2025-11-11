"""gRPC 重试拦截器 - 实现自动重试机制"""
import time
import logging
import grpc
from typing import Callable, Any, Optional, List

logger = logging.getLogger(__name__)


class RetryInterceptor(grpc.UnaryUnaryClientInterceptor, grpc.UnaryStreamClientInterceptor, 
                       grpc.StreamUnaryClientInterceptor, grpc.StreamStreamClientInterceptor):
    """
    gRPC 重试拦截器 - 根据配置自动重试失败的调用
    
    支持指数退避策略和可配置的重试状态码
    只对一元一元调用进行重试，流式调用不重试
    """
    
    def __init__(
        self,
        max_retry_attempts: int = 3,
        initial_backoff: float = 1.0,
        max_backoff: float = 10.0,
        backoff_multiplier: float = 2.0,
        retryable_status_codes: Optional[List[str]] = None
    ):
        """
        初始化重试拦截器
        
        Args:
            max_retry_attempts: 最大重试次数（不包括首次尝试）
            initial_backoff: 初始退避时间（秒）
            max_backoff: 最大退避时间（秒）
            backoff_multiplier: 退避倍数
            retryable_status_codes: 可重试的状态码列表
        """
        self.max_retry_attempts = max_retry_attempts
        self.initial_backoff = initial_backoff
        self.max_backoff = max_backoff
        self.backoff_multiplier = backoff_multiplier
        
        # 将状态码字符串转换为 grpc.StatusCode
        self.retryable_status_codes = set()
        if retryable_status_codes:
            for code_str in retryable_status_codes:
                try:
                    code = getattr(grpc.StatusCode, code_str.upper())
                    self.retryable_status_codes.add(code)
                except AttributeError:
                    logger.warning(f"Unknown gRPC status code: {code_str}")
        
        # 默认可重试的状态码
        if not self.retryable_status_codes:
            self.retryable_status_codes = {
                grpc.StatusCode.UNAVAILABLE,
                grpc.StatusCode.DEADLINE_EXCEEDED,
                grpc.StatusCode.RESOURCE_EXHAUSTED,
                grpc.StatusCode.ABORTED,
                grpc.StatusCode.INTERNAL,
                grpc.StatusCode.UNKNOWN,
            }
    
    def _should_retry(self, status_code: grpc.StatusCode) -> bool:
        """判断是否应该重试"""
        return status_code in self.retryable_status_codes
    
    def _calculate_backoff(self, attempt: int) -> float:
        """计算退避时间"""
        backoff = self.initial_backoff * (self.backoff_multiplier ** attempt)
        return min(backoff, self.max_backoff)
    
    def intercept_unary_unary(
        self,
        continuation: Callable,
        client_call_details: grpc.ClientCallDetails,
        request: Any
    ) -> grpc.Call:
        """
        拦截一元一元调用，实现重试逻辑
        
        通过包装 Call 对象来实现重试，当调用失败时会自动重试
        """
        class RetryableCall(grpc.Call):
            """可重试的 Call 包装器"""
            
            def __init__(self, interceptor, continuation, client_call_details, request):
                self._interceptor = interceptor
                self._continuation = continuation
                self._client_call_details = client_call_details
                self._request = request
                self._call = None
                self._attempt = 0
                self._last_exception = None
                self._result = None
                self._result_retrieved = False
            
            def _make_call(self):
                """创建新的调用"""
                return self._continuation(self._client_call_details, self._request)
            
            def _get_result(self):
                """获取结果，带重试逻辑"""
                if self._result_retrieved:
                    return self._result
                
                while self._attempt <= self._interceptor.max_retry_attempts:
                    try:
                        if self._call is None:
                            self._call = self._make_call()
                        
                        # 尝试获取结果
                        self._result = self._call.result()
                        self._result_retrieved = True
                        return self._result
                        
                    except grpc.RpcError as e:
                        self._last_exception = e
                        status_code = e.code()
                        
                        if not self._interceptor._should_retry(status_code) or self._attempt >= self._interceptor.max_retry_attempts:
                            self._result_retrieved = True
                            raise
                        
                        # 计算退避时间并等待
                        backoff = self._interceptor._calculate_backoff(self._attempt)
                        logger.info(
                            f"gRPC call failed with {status_code}, "
                            f"retrying in {backoff:.2f}s (attempt {self._attempt + 1}/{self._interceptor.max_retry_attempts + 1})"
                        )
                        time.sleep(backoff)
                        self._attempt += 1
                        self._call = None  # 重置调用，准备重试
                
                # 如果所有重试都失败了，抛出最后一个异常
                self._result_retrieved = True
                if self._last_exception:
                    raise self._last_exception
                
                return self._result
            
            def result(self, timeout=None):
                """获取调用结果"""
                return self._get_result()
            
            def exception(self, timeout=None):
                """获取调用异常"""
                try:
                    self._get_result()
                    return None
                except grpc.RpcError as e:
                    return e
            
            def traceback(self, timeout=None):
                """获取调用异常堆栈"""
                try:
                    self._get_result()
                    return None
                except grpc.RpcError as e:
                    import sys
                    return sys.exc_info()[2]
            
            def cancel(self):
                """取消调用"""
                if self._call:
                    self._call.cancel()
            
            def cancelled(self):
                """检查是否已取消"""
                if self._call:
                    return self._call.cancelled()
                return False
            
            def done(self):
                """检查是否完成"""
                if self._call:
                    return self._call.done()
                return False
            
            def time_remaining(self):
                """获取剩余时间"""
                if self._call:
                    return self._call.time_remaining()
                return None
            
            def add_done_callback(self, callback):
                """添加完成回调"""
                if self._call:
                    self._call.add_done_callback(callback)
            
            def add_callback(self, callback):
                """添加回调（add_done_callback 的别名）"""
                self.add_done_callback(callback)
            
            def is_active(self):
                """检查调用是否活跃"""
                if self._call:
                    return self._call.is_active()
                # 如果还没有创建调用，或者调用已完成，返回 False
                return not self._result_retrieved
            
            def initial_metadata(self):
                """获取初始元数据"""
                if self._call:
                    return self._call.initial_metadata()
                return None
            
            def trailing_metadata(self):
                """获取尾部元数据"""
                if self._call:
                    return self._call.trailing_metadata()
                return None
            
            def code(self):
                """获取状态码"""
                if self._call:
                    return self._call.code()
                if self._last_exception:
                    return self._last_exception.code()
                return grpc.StatusCode.OK
            
            def details(self):
                """获取错误详情"""
                if self._call:
                    return self._call.details()
                if self._last_exception:
                    return self._last_exception.details()
                return None
        
        return RetryableCall(self, continuation, client_call_details, request)
    
    def intercept_unary_stream(
        self,
        continuation: Callable,
        client_call_details: grpc.ClientCallDetails,
        request: Any
    ) -> grpc.Call:
        """拦截一元流式调用（不重试，直接传递）"""
        return continuation(client_call_details, request)
    
    def intercept_stream_unary(
        self,
        continuation: Callable,
        client_call_details: grpc.ClientCallDetails,
        request_iterator: Any
    ) -> grpc.Call:
        """拦截流式一元调用（不重试，直接传递）"""
        return continuation(client_call_details, request_iterator)
    
    def intercept_stream_stream(
        self,
        continuation: Callable,
        client_call_details: grpc.ClientCallDetails,
        request_iterator: Any
    ) -> grpc.Call:
        """拦截流式流式调用（不重试，直接传递）"""
        return continuation(client_call_details, request_iterator)


def create_retry_interceptor(
    max_retry_attempts: int = 3,
    initial_backoff: float = 1.0,
    max_backoff: float = 10.0,
    backoff_multiplier: float = 2.0,
    retryable_status_codes: Optional[List[str]] = None
) -> RetryInterceptor:
    """
    创建重试拦截器实例
    
    Args:
        max_retry_attempts: 最大重试次数
        initial_backoff: 初始退避时间（秒）
        max_backoff: 最大退避时间（秒）
        backoff_multiplier: 退避倍数
        retryable_status_codes: 可重试的状态码列表
        
    Returns:
        RetryInterceptor 实例
    """
    return RetryInterceptor(
        max_retry_attempts=max_retry_attempts,
        initial_backoff=initial_backoff,
        max_backoff=max_backoff,
        backoff_multiplier=backoff_multiplier,
        retryable_status_codes=retryable_status_codes
    )

