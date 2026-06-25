from urllib.parse import urlparse

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


IHERB_ALLOWED_DOMAINS = {'kr.iherb.com', 'iherb.com'}


class HealthGoal(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.name


class MedicationOption(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.name


class SpecialConditionOption(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.name


class Report(models.Model):
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = [
        (STATUS_COMPLETED, 'completed'),
        (STATUS_FAILED, 'failed'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reports',
    )
    status = models.CharField(max_length=32, choices=STATUS_CHOICES)
    title = models.CharField(max_length=255)
    input_summary = models.JSONField(default=dict)
    recommended_ingredients = models.JSONField(default=list)
    lifestyle_tips = models.JSONField(default=list)
    disclaimer = models.TextField()
    citations = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at', '-id']

    def __str__(self):
        return self.title


class ReportMessage(models.Model):
    ROLE_USER = 'user'
    ROLE_ASSISTANT = 'assistant'

    ROLE_CHOICES = [
        (ROLE_USER, 'user'),
        (ROLE_ASSISTANT, 'assistant'),
    ]

    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    role = models.CharField(max_length=32, choices=ROLE_CHOICES)
    content = models.TextField()
    guardrail_result = models.JSONField(default=dict, blank=True)
    citations = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at', 'id']

    def __str__(self):
        return f'{self.report_id} - {self.role}'


class IngredientLinkMapping(models.Model):
    """
    성분별 iHerb 링크 매핑 테이블.
    normalized_name 기준으로 조회하며, allowlist 도메인만 저장/노출한다.
    """

    normalized_name = models.CharField(max_length=100, unique=True)
    ingredient_name_ko = models.CharField(max_length=100)
    ingredient_name_en = models.CharField(max_length=100, blank=True, default='')
    iherb_url = models.URLField(max_length=500)
    iherb_category_name = models.CharField(max_length=200, blank=True, default='')
    is_active = models.BooleanField(default=True)
    last_verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['normalized_name']

    def __str__(self):
        return self.normalized_name

    def is_url_allowed(self) -> bool:
        """저장된 iherb_url이 허용된 도메인인지 검증한다."""
        try:
            parsed = urlparse(self.iherb_url)
            return parsed.scheme == 'https' and parsed.netloc in IHERB_ALLOWED_DOMAINS
        except Exception:
            return False

    def clean(self):
        super().clean()
        if not self.is_url_allowed():
            raise ValidationError({
                'iherb_url': '허용된 iHerb HTTPS 도메인 URL만 저장할 수 있습니다.'
            })
