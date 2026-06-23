from rest_framework import generics, permissions

from .models import HealthGoal, MedicationOption, SpecialConditionOption
from .serializers import (
    HealthGoalSerializer,
    MedicationOptionSerializer,
    SpecialConditionOptionSerializer,
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