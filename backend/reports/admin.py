from django.contrib import admin

from .models import HealthGoal, MedicationOption, Report, ReportMessage, SpecialConditionOption


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


@admin.register(ReportMessage)
class ReportMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'report', 'role', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['content', 'report__title', 'report__user__email']
    readonly_fields = ['created_at']
