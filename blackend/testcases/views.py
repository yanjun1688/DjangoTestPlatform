from django.shortcuts import render
from rest_framework import viewsets
from .models import TestCase, TestPlan
from .serializers import TestCaseSerializer, TestPlanSerializer
from .permissions import IsAdminOrReadOnly

# Create your views here.

class TestCaseViewSet(viewsets.ModelViewSet):
    queryset = TestCase.objects.all()
    serializer_class = TestCaseSerializer
    permission_classes = [IsAdminOrReadOnly]

class TestPlanViewSet(viewsets.ModelViewSet):
    queryset = TestPlan.objects.all()
    serializer_class = TestPlanSerializer
    permission_classes = [IsAdminOrReadOnly]
