from rest_framework import serializers

from .models import HealthGoal, MedicationOption, Report, ReportMessage, SpecialConditionOption


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


class ReportHealthGoalInputSerializer(serializers.Serializer):
    code = serializers.CharField()
    priority = serializers.IntegerField(min_value=1)


class ReportOptionInputSerializer(serializers.Serializer):
    code = serializers.CharField()
    name = serializers.CharField(required=False, allow_blank=True)


class ReportCreateSerializer(serializers.Serializer):
    age = serializers.IntegerField(min_value=1, max_value=150)
    gender = serializers.ChoiceField(choices=['female', 'male', 'other'])
    health_goals = ReportHealthGoalInputSerializer(many=True)
    medications = ReportOptionInputSerializer(many=True, required=False)
    special_conditions = ReportOptionInputSerializer(many=True, required=False)
    additional_notes = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    def validate_health_goals(self, value):
        if not value:
            raise serializers.ValidationError('최소 1개 이상 선택해야 합니다.')
        if len(value) > 5:
            raise serializers.ValidationError('최대 5개까지 선택할 수 있습니다.')

        priorities = [item['priority'] for item in value]
        expected_priorities = list(range(1, len(value) + 1))

        if sorted(priorities) != expected_priorities:
            raise serializers.ValidationError(
                '우선순위는 1부터 선택 개수까지 순서대로 입력해야 합니다.'
            )

        codes = [item['code'] for item in value]
        existing_options = HealthGoal.objects.filter(
            code__in=codes,
            is_active=True,
        )
        option_map = {option.code: option for option in existing_options}

        invalid_codes = [code for code in codes if code not in option_map]
        if invalid_codes:
            raise serializers.ValidationError(f'유효하지 않은 code입니다: {invalid_codes}')

        return [
            {
                'code': item['code'],
                'name': option_map[item['code']].name,
                'priority': item['priority'],
            }
            for item in value
        ]

    def validate_medications(self, value):
        return self._validate_options(value, MedicationOption)

    def validate_special_conditions(self, value):
        return self._validate_options(value, SpecialConditionOption)

    def _validate_options(self, value, model):
        codes = [item['code'] for item in value]
        existing_options = model.objects.filter(code__in=codes, is_active=True)
        option_map = {option.code: option for option in existing_options}

        invalid_codes = [code for code in codes if code not in option_map]
        if invalid_codes:
            raise serializers.ValidationError(f'유효하지 않은 code입니다: {invalid_codes}')

        return [
            {
                'code': item['code'],
                'name': option_map[item['code']].name,
            }
            for item in value
        ]


class ReportListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'title', 'status', 'created_at']


class ReportDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = [
            'id',
            'status',
            'title',
            'input_summary',
            'recommended_ingredients',
            'lifestyle_tips',
            'disclaimer',
            'citations',
            'created_at',
        ]


class ReportTitleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'title']
        read_only_fields = ['id']


class ReportMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportMessage
        fields = [
            'id',
            'role',
            'content',
            'guardrail_result',
            'citations',
            'created_at',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if instance.role == ReportMessage.ROLE_USER:
            data.pop('guardrail_result', None)
            data.pop('citations', None)

        if instance.role == ReportMessage.ROLE_ASSISTANT and not data.get('guardrail_result'):
            data.pop('guardrail_result', None)

        return data


class ReportMessageCreateSerializer(serializers.Serializer):
    content = serializers.CharField(
        allow_blank=False,
        trim_whitespace=True,
        max_length=2000,
    )
