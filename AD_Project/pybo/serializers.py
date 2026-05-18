from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Bookmark, Question


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class QuestionSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    vote_count = serializers.SerializerMethodField()
    answer_count = serializers.SerializerMethodField()
    bookmark_count = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            'id',
            'subject',
            'content',
            'author',
            'create_date',
            'modify_date',
            'vote_count',
            'answer_count',
            'bookmark_count',
        ]

    def get_vote_count(self, obj):
        return getattr(obj, 'vote_count', obj.voter.count())

    def get_answer_count(self, obj):
        return getattr(obj, 'answer_count', obj.answer_set.count())

    def get_bookmark_count(self, obj):
        return getattr(obj, 'bookmark_count', obj.bookmarks.count())


class BookmarkSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(read_only=True)

    class Meta:
        model = Bookmark
        fields = ['id', 'question', 'create_date']
