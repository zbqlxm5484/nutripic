from django.contrib import admin

from .models import HealthGoal, IngredientLinkMapping, MedicationOption, Report, ReportMessage, SpecialConditionOption


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


@admin.register(IngredientLinkMapping)
class IngredientLinkMappingAdmin(admin.ModelAdmin):
    list_display = ['id', 'normalized_name', 'ingredient_name_ko', 'ingredient_name_en', 'iherb_url', 'iherb_category_name', 'is_active', 'last_verified_at', 'is_url_allowed']
    list_editable = ['is_active']
    list_filter = ['is_active']
    search_fields = ['normalized_name', 'ingredient_name_ko', 'ingredient_name_en']

    @admin.display(boolean=True, description='URL 허용 여부')
    def is_url_allowed(self, obj):
        return obj.is_url_allowed()
