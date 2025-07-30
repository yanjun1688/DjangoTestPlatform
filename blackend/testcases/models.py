from django.db import models
from django.conf import settings
from mptt.models import MPTTModel, TreeForeignKey
import reversion
import csv
import json
import os

@reversion.register()
class TestCase(MPTTModel):
    title = models.CharField(max_length=200, unique=True)
    precondition = models.TextField(blank=True)
    description = models.TextField(blank=True)
    STATUS_CHOICES = [
        ('passed', '通过'),
        ('failed', '失败'),
        ('blocked', '阻塞'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='blocked')
    module = models.CharField(max_length=100, blank=True)
    PRIORITY_CHOICES = [
        ('P0', '高'),
        ('P1', '中'),
        ('P2', '低'),
    ]
    priority = models.CharField(max_length=2, choices=PRIORITY_CHOICES, default='P1')
    tags = models.CharField(max_length=200, blank=True)
    version = models.CharField(max_length=20, default='v1.0')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    requirement_link = models.CharField(max_length=200, blank=True, help_text='需求ID或外部链接')
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='testcases')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class MPTTMeta:
        order_insertion_by = ['title']

    def __str__(self):
        return self.title

class TestPlan(models.Model):
    name = models.CharField(max_length=200)
    test_cases = models.ManyToManyField(TestCase, related_name='plans', blank=True)
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='testplans')
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    STATUS_CHOICES = [
        ('pending', '待执行'),
        ('running', '进行中'),
        ('completed', '已完成'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class TestDataFile(models.Model):
    """测试数据文件模型，用于数据驱动测试"""
    name = models.CharField(max_length=255, verbose_name='文件名称')
    test_case = models.OneToOneField(
        TestCase,
        on_delete=models.CASCADE,
        related_name='data_file',
        verbose_name='关联测试用例'
    )
    file = models.FileField(
        upload_to='testdata/%Y/%m/%d/',
        verbose_name='数据文件'
    )
    FILE_TYPE_CHOICES = [
        ('csv', 'CSV'),
        ('json', 'JSON'),
    ]
    file_type = models.CharField(
        max_length=10,
        choices=FILE_TYPE_CHOICES,
        verbose_name='文件类型'
    )
    description = models.TextField(blank=True, verbose_name='文件描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '测试数据文件'
        verbose_name_plural = '测试数据文件'

    def __str__(self):
        return f"{self.name} ({self.file_type.upper()})"

    def get_file_size(self):
        """获取文件大小（字节）"""
        try:
            return self.file.size
        except (ValueError, OSError):
            return 0

    def get_file_size_display(self):
        """获取友好的文件大小显示"""
        size = self.get_file_size()
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"

    def parse_file(self, max_rows=None):
        """
        解析文件内容
        
        Args:
            max_rows: 最大读取行数，用于预览时限制数据量
            
        Returns:
            dict: 包含headers和rows的字典
        """
        if not self.file:
            return {'headers': [], 'rows': []}

        try:
            if self.file_type == 'csv':
                return self._parse_csv(max_rows)
            elif self.file_type == 'json':
                return self._parse_json(max_rows)
            else:
                raise ValueError(f"不支持的文件类型: {self.file_type}")
        except Exception as e:
            raise ValueError(f"文件解析失败: {str(e)}")

    def _parse_csv(self, max_rows=None):
        """解析CSV文件"""
        headers = []
        rows = []
        
        self.file.seek(0)  # 重置文件指针
        
        # 尝试不同的编码
        content = None
        for encoding in ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']:
            try:
                self.file.seek(0)
                content = self.file.read().decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            raise ValueError("无法解码文件，请检查文件编码")
        
        # 使用csv模块解析
        from io import StringIO
        csv_file = StringIO(content)
        reader = csv.reader(csv_file)
        
        # 读取表头
        try:
            headers = next(reader)
        except StopIteration:
            return {'headers': [], 'rows': []}
        
        # 读取数据行
        for i, row in enumerate(reader):
            if max_rows and i >= max_rows:
                break
            # 确保行的长度与表头一致
            while len(row) < len(headers):
                row.append('')
            rows.append(row[:len(headers)])
        
        return {'headers': headers, 'rows': rows}

    def _parse_json(self, max_rows=None):
        """解析JSON文件"""
        self.file.seek(0)
        
        try:
            content = self.file.read().decode('utf-8')
            data = json.loads(content)
        except UnicodeDecodeError:
            raise ValueError("JSON文件编码错误，请使用UTF-8编码")
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON格式错误: {str(e)}")
        
        if not isinstance(data, list):
            raise ValueError("JSON文件必须是对象数组格式")
        
        if not data:
            return {'headers': [], 'rows': []}
        
        # 获取所有可能的键作为表头
        headers = set()
        for item in data:
            if isinstance(item, dict):
                headers.update(item.keys())
            else:
                raise ValueError("JSON数组中的每个元素必须是对象")
        
        headers = sorted(list(headers))
        
        # 转换为行数据
        rows = []
        for i, item in enumerate(data):
            if max_rows and i >= max_rows:
                break
            row = [str(item.get(header, '')) for header in headers]
            rows.append(row)
        
        return {'headers': headers, 'rows': rows}

    def get_data_count(self):
        """获取数据行数"""
        try:
            parsed = self.parse_file()
            return len(parsed['rows'])
        except:
            return 0

    def get_preview_data(self, max_rows=5):
        """获取预览数据"""
        return self.parse_file(max_rows=max_rows)

    def validate_file(self):
        """验证文件格式和内容"""
        errors = []
        
        if not self.file:
            errors.append("请选择文件")
            return errors
        
        # 检查文件扩展名
        file_extension = os.path.splitext(self.file.name)[1].lower()
        if self.file_type == 'csv' and file_extension not in ['.csv']:
            errors.append("CSV文件扩展名必须是.csv")
        elif self.file_type == 'json' and file_extension not in ['.json']:
            errors.append("JSON文件扩展名必须是.json")
        
        # 检查文件大小（限制10MB）
        max_size = 10 * 1024 * 1024  # 10MB
        if self.get_file_size() > max_size:
            errors.append(f"文件大小不能超过10MB，当前大小: {self.get_file_size_display()}")
        
        # 尝试解析文件
        try:
            parsed = self.parse_file(max_rows=1)
            if not parsed['headers']:
                errors.append("文件中没有找到有效的表头数据")
        except Exception as e:
            errors.append(f"文件格式错误: {str(e)}")
        
        return errors
