import re

from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from reviews.models import Category, Comment, Genre, Review, Title
from user.models import User


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.CharField(max_length=150,
                                     required=True)

    def validate_username(self, value):
        if not re.fullmatch(r'[\w\@\.\+\-]+', value):
            raise serializers.ValidationError('Запрещено.')
        if value == 'me':
            raise serializers.ValidationError(
                'Использование имени me запрещено.'
            )
        return value

    def validate(self, data):
        if_username = User.objects.filter(
            username__iexact=data['username']).exists()
        if_email = User.objects.filter(email__iexact=data['email']).exists()
        if User.objects.filter(username__iexact=data['username'],
                               email__iexact=data['email']).exists():
            return data
        if if_username:
            raise serializers.ValidationError('Такой ник уже зарегистрирован')
        if if_email:
            raise serializers.ValidationError('Почта уже использовалась')
        return data


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=80, required=True)
    email = serializers.CharField(max_length=80, required=True)
    role = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = User
        fields = ('username',
                  'email',
                  'first_name',
                  'last_name',
                  'bio',
                  'role')

    def validate_role(self, attrs):
        user = get_object_or_404(User, id=id)
        if user.is_admin and 'role' in attrs and not user.is_superuser:
            attrs['role'] = 'user'
        return super().validate(attrs)

    def validate_username(self, value):
        if not re.fullmatch(r'[\w\@\.\+\-]+', value):
            raise serializers.ValidationError('Запрещено.')
        if value == 'me':
            raise serializers.ValidationError(
                'Использование имени me запрещено.'
            )
        return value


class AdminUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )

    def validate_username(self, value):
        if not re.fullmatch(r'[\w\@\.\+\-]+', value):
            raise serializers.ValidationError('Запрещено.')
        if value == 'me':
            raise serializers.ValidationError(
                'Использование имени me запрещено.'
            )
        return value


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug',)


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True, queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    class Meta:
        fields = '__all__'
        model = Title


class ReadOnlyTitleSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(read_only=True)
    genre = GenreSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if request.method == 'POST':
            if Review.objects.filter(title=title, author=author).exists():
                raise ValidationError('Нельзя оставить больше одного отзыва')
        return data

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('title',)


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.SlugRelatedField(
        slug_field='text',
        read_only=True
    )

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = '__all__'
