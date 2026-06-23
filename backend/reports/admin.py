from django.contrib import admin

from .models import HealthGoal, MedicationOption, SpecialConditionOption


@admin.register(HealthGoal)
class HealthGoalAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['code', 'name']


@admin.register(MedicationOption)
class MedicationOptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['code', 'name']


@admin.register(SpecialConditionOption)
class SpecialConditionOptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['code', 'name']