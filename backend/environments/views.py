from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Q
from .models import Environment, EnvironmentVariable, EnvironmentUsageLog
from .serializers import (
    EnvironmentSerializer, EnvironmentListSerializer, 
    EnvironmentVariableSerializer, EnvironmentVariableCreateSerializer,
    EnvironmentUsageLogSerializer
)
from testcases.permissions import IsAdminOrReadOnly


class EnvironmentViewSet(viewsets.ModelViewSet):
    """环境管理ViewSet"""
    permission_classes = [IsAdminOrReadOnly]  # 使用统一的权限控制
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'is_default']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['-is_default', '-created_at']

    def get_queryset(self):
        """获取当前用户的环境列表"""
        return Environment.objects.filter(created_by=self.request.user)

    def get_serializer_class(self):
        """根据操作选择序列化器"""
        if self.action == 'list':
            return EnvironmentListSerializer
        return EnvironmentSerializer

    def perform_create(self, serializer):
        """创建环境时设置创建者"""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """设置为默认环境"""
        environment = self.get_object()
        
        # 将用户的其他环境设置为非默认
        Environment.objects.filter(
            created_by=request.user,
            is_default=True
        ).update(is_default=False)
        
        # 设置当前环境为默认
        environment.is_default = True
        environment.save()
        
        return Response({'message': f'已将 "{environment.name}" 设置为默认环境'})

    @action(detail=True, methods=['post'])
    def clone(self, request, pk=None):
        """克隆环境"""
        source_env = self.get_object()
        
        # 创建新环境
        new_env = Environment.objects.create(
            name=f"{source_env.name} (副本)",
            description=f"克隆自 {source_env.name}",
            is_active=True,
            is_default=False,
            created_by=request.user
        )
        
        # 复制所有变量
        for variable in source_env.variables.all():
            EnvironmentVariable.objects.create(
                environment=new_env,
                key=variable.key,
                value=variable.value,
                description=variable.description,
                is_secret=variable.is_secret
            )
        
        serializer = self.get_serializer(new_env)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'post'])
    def variables(self, request, pk=None):
        """管理环境变量"""
        environment = self.get_object()
        
        if request.method == 'GET':
            variables = environment.variables.all()
            serializer = EnvironmentVariableSerializer(
                variables, many=True, context={'request': request}
            )
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = EnvironmentVariableCreateSerializer(
                data=request.data,
                context={'request': request, 'environment_id': environment.id}
            )
            if serializer.is_valid():
                serializer.save(environment=environment)
                # 返回完整的变量信息
                variable_serializer = EnvironmentVariableSerializer(
                    serializer.instance, context={'request': request}
                )
                return Response(variable_serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def replace_variables(self, request, pk=None):
        """替换文本中的环境变量"""
        environment = self.get_object()
        text = request.data.get('text', '')
        
        if not text:
            return Response({'error': '请提供要替换的文本'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取环境变量字典
        variables = {}
        for var in environment.variables.all():
            variables[var.key] = var.value
        
        # 替换变量
        import re
        def replace_var(match):
            var_name = match.group(1)
            return variables.get(var_name, match.group(0))
        
        replaced_text = re.sub(r'\{\{(\w+)\}\}', replace_var, text)
        
        return Response({
            'original_text': text,
            'replaced_text': replaced_text,
            'variables_used': list(re.findall(r'\{\{(\w+)\}\}', text))
        })

    @action(detail=False, methods=['get'])
    def usage_stats(self, request):
        """获取环境使用统计"""
        user_environments = self.get_queryset()
        
        stats = []
        for env in user_environments:
            usage_count = env.usage_logs.count()
            recent_usage = env.usage_logs.first()
            
            stats.append({
                'environment': EnvironmentListSerializer(env).data,
                'usage_count': usage_count,
                'last_used': recent_usage.used_at if recent_usage else None,
                'last_action': recent_usage.get_action_display() if recent_usage else None
            })
        
        return Response(stats)


class EnvironmentVariableViewSet(viewsets.ModelViewSet):
    """环境变量管理ViewSet"""
    serializer_class = EnvironmentVariableSerializer
    permission_classes = [IsAdminOrReadOnly]  # 使用统一的权限控制

    def get_queryset(self):
        """获取当前用户环境的变量"""
        return EnvironmentVariable.objects.filter(
            environment__created_by=self.request.user
        )

    def get_serializer_class(self):
        """根据操作选择序列化器"""
        if self.action in ['create', 'update', 'partial_update']:
            return EnvironmentVariableCreateSerializer
        return EnvironmentVariableSerializer

    def update(self, request, *args, **kwargs):
        """更新变量时传递环境ID"""
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, 
            data=request.data, 
            partial=kwargs.get('partial', False),
            context={
                'request': request, 
                'environment_id': instance.environment.id
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # 返回完整的变量信息
        response_serializer = EnvironmentVariableSerializer(
            instance, context={'request': request}
        )
        return Response(response_serializer.data)


def log_environment_usage(environment, user, action, context=None):
    """记录环境使用日志的辅助函数"""
    EnvironmentUsageLog.objects.create(
        environment=environment,
        user=user,
        action=action,
        context=context or {}
    )