from django import forms

from pybo.models import Question, Answer, Comment


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['category', 'subject', 'content']
        labels = {
            'category': '카테고리',
            'subject': '제목',
            'content': '내용',
        }
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
        }


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content']
        labels = {
            'content': '답변내용',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        labels = {
            'content': '댓글내용',
        }
