from django import forms

from pybo.models import Question, Answer, Comment, ContentReport


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['category', 'subject', 'content']
        labels = {
            'category': '질문 유형',
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


class ContentReportForm(forms.ModelForm):
    class Meta:
        model = ContentReport
        fields = ['reason', 'content']
        labels = {
            'reason': '신고 사유',
            'content': '상세 내용',
        }
        widgets = {
            'reason': forms.Select(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }


class ContentReportReviewForm(forms.ModelForm):
    class Meta:
        model = ContentReport
        fields = ['status', 'review_memo']
        labels = {
            'status': '처리 상태',
            'review_memo': '검토 메모',
        }
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'review_memo': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }
