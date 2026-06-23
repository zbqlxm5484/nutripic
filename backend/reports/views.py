from rest_framework import generics, permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import HealthGoal, MedicationOption, Report, ReportMessage, SpecialConditionOption
from .services import generate_report, generate_report_chat_response
from .serializers import (
    HealthGoalSerializer,
    MedicationOptionSerializer,
    SpecialConditionOptionSerializer,
    ReportCreateSerializer,
    ReportDetailSerializer,
    ReportListSerializer,
    ReportTitleUpdateSerializer,
    ReportMessageSerializer,
    ReportMessageCreateSerializer,
)


class HealthGoalListView(generics.ListAPIView):
    queryset = HealthGoal.objects.filter(is_active=True)
    serializer_class = HealthGoalSerializer
    permission_classes = [permissions.AllowAny]


class MedicationOptionListView(generics.ListAPIView):
    queryset = MedicationOption.objects.filter(is_active=True)
    serializer_class = MedicationOptionSerializer
    permission_classes = [permissions.AllowAny]


class SpecialConditionOptionListView(generics.ListAPIView):
    queryset = SpecialConditionOption.objects.filter(is_active=True)
    serializer_class = SpecialConditionOptionSerializer
    permission_classes = [permissions.AllowAny]


class ReportPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ReportListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ReportPagination
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        return Report.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ReportListSerializer
        return ReportCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = ReportCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = generate_report(serializer.validated_data)

        if result['status'] == 'needs_clarification':
            return Response(result, status=status.HTTP_200_OK)

        report = Report.objects.create(
            user=request.user,
            status=result['status'],
            title=result['title'],
            input_summary=result['input_summary'],
            recommended_ingredients=result['recommended_ingredients'],
            lifestyle_tips=result['lifestyle_tips'],
            disclaimer=result['disclaimer'],
            citations=result['citations'],
        )

        response_serializer = ReportDetailSerializer(report)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class ReportDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = 'report_id'
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        return Report.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return ReportTitleUpdateSerializer
        return ReportDetailSerializer


class ReportMessageListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options']

    def get_report(self):
        return get_object_or_404(
            Report,
            id=self.kwargs['report_id'],
            user=self.request.user,
        )

    def get_queryset(self):
        report = self.get_report()
        return ReportMessage.objects.filter(report=report)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReportMessageCreateSerializer
        return ReportMessageSerializer

    def create(self, request, *args, **kwargs):
        report = self.get_report()

        serializer = ReportMessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_message = ReportMessage.objects.create(
            report=report,
            role=ReportMessage.ROLE_USER,
            content=serializer.validated_data['content'],
        )

        result = generate_report_chat_response(
            report=report,
            content=user_message.content,
        )

        assistant_message = ReportMessage.objects.create(
            report=report,
            role=ReportMessage.ROLE_ASSISTANT,
            content=result['content'],
            guardrail_result=result.get('guardrail_result', {}),
            citations=result.get('citations', []),
        )

        response_serializer = ReportMessageSerializer(assistant_message)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
