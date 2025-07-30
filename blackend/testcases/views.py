from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import Http404
from .models import TestCase, TestPlan, TestDataFile
from .serializers import (
    TestCaseSerializer, TestPlanSerializer, 
    TestDataFileSerializer, TestDataFileUploadSerializer
)
from .permissions import IsAdminOrReadOnly

# Create your views here.

class TestCaseViewSet(viewsets.ModelViewSet):
    queryset = TestCase.objects.all()
    serializer_class = TestCaseSerializer
    permission_classes = [IsAdminOrReadOnly]

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def datafile(self, request, pk=None):
        """上传或更新数据文件"""
        test_case = self.get_object()
        
        # 检查是否已存在数据文件
        try:
            existing_file = test_case.data_file
            # 如果存在，删除旧文件并更新
            if existing_file.file:
                existing_file.file.delete()
            existing_file.delete()
        except TestDataFile.DoesNotExist:
            pass
        
        # 创建新的数据文件
        serializer = TestDataFileUploadSerializer(data=request.data)
        if serializer.is_valid():
            data_file = serializer.save(test_case=test_case)
            
            # 返回完整的数据文件信息
            response_serializer = TestDataFileSerializer(data_file)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def datafile_delete(self, request, pk=None):
        """删除数据文件"""
        test_case = self.get_object()
        
        try:
            data_file = test_case.data_file
            # 删除文件
            if data_file.file:
                data_file.file.delete()
            data_file.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except TestDataFile.DoesNotExist:
            return Response(
                {'error': '数据文件不存在'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'])
    def datafile_preview(self, request, pk=None):
        """预览数据文件内容"""
        test_case = self.get_object()
        
        try:
            data_file = test_case.data_file
            
            # 获取预览行数参数
            max_rows = int(request.query_params.get('rows', 5))
            max_rows = min(max_rows, 50)  # 最多50行
            
            try:
                preview_data = data_file.get_preview_data(max_rows=max_rows)
                
                response_data = {
                    'file_info': {
                        'id': data_file.id,
                        'name': data_file.name,
                        'file_type': data_file.file_type,
                        'file_size': data_file.get_file_size_display(),
                        'total_rows': data_file.get_data_count(),
                    },
                    'preview': preview_data,
                    'preview_rows': len(preview_data.get('rows', []))
                }
                
                return Response(response_data)
                
            except Exception as e:
                return Response(
                    {'error': f'文件解析失败: {str(e)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except TestDataFile.DoesNotExist:
            return Response(
                {'error': '数据文件不存在'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'])
    def datafile_info(self, request, pk=None):
        """获取数据文件信息"""
        test_case = self.get_object()
        
        try:
            data_file = test_case.data_file
            serializer = TestDataFileSerializer(data_file)
            return Response(serializer.data)
        except TestDataFile.DoesNotExist:
            return Response(
                {'error': '数据文件不存在'}, 
                status=status.HTTP_404_NOT_FOUND
            )

class TestPlanViewSet(viewsets.ModelViewSet):
    queryset = TestPlan.objects.all()
    serializer_class = TestPlanSerializer
    permission_classes = [IsAdminOrReadOnly]

class TestDataFileViewSet(viewsets.ModelViewSet):
    """数据文件管理视图集"""
    queryset = TestDataFile.objects.all()
    serializer_class = TestDataFileSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TestDataFileUploadSerializer
        return TestDataFileSerializer

    def destroy(self, request, *args, **kwargs):
        """删除数据文件时同时删除物理文件"""
        instance = self.get_object()
        if instance.file:
            instance.file.delete()
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        """预览数据文件"""
        data_file = self.get_object()
        max_rows = int(request.query_params.get('rows', 5))
        max_rows = min(max_rows, 50)
        
        try:
            preview_data = data_file.get_preview_data(max_rows=max_rows)
            return Response({
                'headers': preview_data['headers'],
                'rows': preview_data['rows'],
                'total_rows': data_file.get_data_count(),
                'preview_rows': len(preview_data['rows'])
            })
        except Exception as e:
            return Response(
                {'error': f'文件解析失败: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
