from rest_framework import serializers

from .models import HealthGoal, MedicationOption, SpecialConditionOption


class HealthGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthGoal
        fields = ['code', 'name']


class MedicationOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicationOption
        fields = ['code', 'name']


class SpecialConditionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialConditionOption
        fields = ['code', 'name']