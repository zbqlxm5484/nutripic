from rest_framework import serializers

from .models import Comment, Post


class AuthorSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)


class PostListSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'author',
            'like_count',
            'comment_count',
            'created_at',
        ]


class PostDetailSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'content',
            'author',
            'like_count',
            'comment_count',
            'is_liked',
            'created_at',
            'updated_at',
        ]

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.likes.filter(user=request.user).exists()


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'content']

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError('Title must not be blank.')
        return value

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError('Content must not be blank.')
        return value


class ReplySerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    parent_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id',
            'author',
            'content',
            'parent_id',
            'created_at',
            'updated_at',
        ]


class CommentSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    parent_id = serializers.IntegerField(read_only=True)
    replies = ReplySerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id',
            'author',
            'content',
            'parent_id',
            'replies',
            'created_at',
            'updated_at',
        ]


class CommentCreateSerializer(serializers.ModelSerializer):
    parent_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Comment
        fields = ['content', 'parent_id']

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError('Content must not be blank.')
        return value

    def validate_parent_id(self, value):
        if value is None:
            return value

        post = self.context['post']

        try:
            parent = Comment.objects.get(id=value, post=post)
        except Comment.DoesNotExist as exc:
            raise serializers.ValidationError('Parent comment does not exist.') from exc

        if parent.parent_id is not None:
            raise serializers.ValidationError('Replies to replies are not allowed.')

        return value

    def create(self, validated_data):
        parent_id = validated_data.pop('parent_id', None)
        parent = None

        if parent_id is not None:
            parent = Comment.objects.get(id=parent_id, post=self.context['post'])

        return Comment.objects.create(
            post=self.context['post'],
            author=self.context['request'].user,
            parent=parent,
            **validated_data,
        )


class CommentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content']

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError('Content must not be blank.')
        return value
