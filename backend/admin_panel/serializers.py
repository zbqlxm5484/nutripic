from rest_framework import serializers

from community.models import Comment, Post


class AdminUserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(read_only=True)
    username = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True, allow_null=True)
    gender = serializers.CharField(read_only=True, allow_null=True)
    role = serializers.CharField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    post_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    report_count = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(source='date_joined', read_only=True)


class AdminUserUpdateSerializer(serializers.Serializer):
    is_active = serializers.BooleanField()


class AdminAuthorSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)


class AdminPostSerializer(serializers.ModelSerializer):
    author = AdminAuthorSerializer(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'content',
            'author',
            'like_count',
            'comment_count',
            'created_at',
            'updated_at',
        ]


class AdminPostSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)


class AdminCommentSerializer(serializers.ModelSerializer):
    author = AdminAuthorSerializer(read_only=True)
    post = AdminPostSummarySerializer(read_only=True)
    parent_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id',
            'post',
            'author',
            'parent_id',
            'content',
            'created_at',
            'updated_at',
        ]