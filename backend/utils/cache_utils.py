"""
缓存工具模块
提供简单的缓存机制来提升API性能
"""

from django.core.cache import cache
from django.conf import settings
import hashlib
import json
from functools import wraps


def cache_key_generator(*args, **kwargs):
    """生成缓存键"""
    key_data = str(args) + str(sorted(kwargs.items()))
    return hashlib.md5(key_data.encode()).hexdigest()


def cache_response(timeout=300, key_prefix='api'):
    """
    缓存API响应的装饰器
    
    Args:
        timeout: 缓存超时时间（秒），默认5分钟
        key_prefix: 缓存键前缀
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{key_prefix}:{func.__name__}:{cache_key_generator(*args, **kwargs)}"
            
            # 尝试从缓存获取
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            
            # 检查结果是否可序列化（避免DRF Response对象问题）
            try:
                # 如果是DRF Response对象，不进行缓存
                from rest_framework.response import Response as DRFResponse
                if isinstance(result, DRFResponse):
                    return result
                    
                # 尝试缓存其他类型的结果
                cache.set(cache_key, result, timeout)
            except Exception:
                # 如果缓存失败，直接返回结果
                pass
                
            return result
            
        return wrapper
    return decorator


def cache_queryset_count(model_class, filters=None, timeout=180):
    """
    缓存查询集计数
    
    Args:
        model_class: 模型类
        filters: 过滤条件字典
        timeout: 缓存超时时间（秒），默认3分钟
    """
    cache_key = f"count:{model_class.__name__}:{cache_key_generator(filters or {})}"
    
    cached_count = cache.get(cache_key)
    if cached_count is not None:
        return cached_count
    
    queryset = model_class.objects.all()
    if filters:
        queryset = queryset.filter(**filters)
    
    count = queryset.count()
    cache.set(cache_key, count, timeout)
    return count


def invalidate_cache_pattern(pattern):
    """
    使用模式匹配失效缓存
    注意：这需要Redis作为缓存后端
    """
    try:
        from django.core.cache.backends.redis import RedisCache
        if isinstance(cache, RedisCache):
            # 使用Redis的KEYS命令查找匹配的键
            redis_client = cache._cache.get_client(1)
            keys = redis_client.keys(f"*{pattern}*")
            if keys:
                redis_client.delete(*keys)
                return len(keys)
    except ImportError:
        pass
    
    return 0


def cache_user_permissions(user_id, timeout=600):
    """
    缓存用户权限信息
    
    Args:
        user_id: 用户ID
        timeout: 缓存超时时间（秒），默认10分钟
    """
    cache_key = f"user_permissions:{user_id}"
    
    cached_permissions = cache.get(cache_key)
    if cached_permissions is not None:
        return cached_permissions
    
    # 这里可以添加具体的权限查询逻辑
    # 暂时返回空字典
    permissions = {}
    cache.set(cache_key, permissions, timeout)
    return permissions


def cache_environment_variables(environment_id, timeout=300):
    """
    缓存环境变量
    
    Args:
        environment_id: 环境ID
        timeout: 缓存超时时间（秒），默认5分钟
    """
    cache_key = f"env_vars:{environment_id}"
    
    cached_vars = cache.get(cache_key)
    if cached_vars is not None:
        return cached_vars
    
    try:
        from environments.models import Environment
        environment = Environment.objects.prefetch_related('variables').get(id=environment_id)
        variables = {var.key: var.value for var in environment.variables.all()}
        cache.set(cache_key, variables, timeout)
        return variables
    except Environment.DoesNotExist:
        return {}


class CacheStats:
    """缓存统计工具"""
    
    @staticmethod
    def get_cache_info():
        """获取缓存统计信息"""
        try:
            if hasattr(cache, '_cache') and hasattr(cache._cache, 'get_stats'):
                return cache._cache.get_stats()
        except:
            pass
        
        return {
            'cache_backend': str(type(cache)),
            'available': True
        }
    
    @staticmethod
    def clear_all_cache():
        """清空所有缓存"""
        try:
            cache.clear()
            return True
        except:
            return False


# 常用的缓存装饰器实例
cache_short = cache_response(timeout=60, key_prefix='short')    # 1分钟
cache_medium = cache_response(timeout=300, key_prefix='medium') # 5分钟
cache_long = cache_response(timeout=900, key_prefix='long')     # 15分钟