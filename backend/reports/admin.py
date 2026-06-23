from django.contrib import admin

from .models import HealthGoal, MedicationOption, Report, SpecialConditionOption


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

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'user__email', 'user__username']
    readonly_fields = ['created_at', 'updated_at']