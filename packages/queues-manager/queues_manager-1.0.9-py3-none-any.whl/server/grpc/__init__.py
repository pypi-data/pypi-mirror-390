"""gRPC 服务模块"""
from server.grpc.service import QueueServiceServicer, serve

__all__ = ["QueueServiceServicer", "serve"]

