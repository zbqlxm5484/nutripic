from django.urls import path

from .views import (
    HealthGoalListView,
    MedicationOptionListView,
    SpecialConditionOptionListView,
)

urlpatterns = [
    path('health_goals/', HealthGoalListView.as_view(), name='health-goal-list'),
    path('medication_options/', MedicationOptionListView.as_view(), name='medication-option-list'),
    path('special_condition_options/', SpecialConditionOptionListView.as_view(), name='special-condition-option-list'),
]