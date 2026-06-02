from django.db import migrations


QUESTION_TYPE_CATEGORIES = [
    ('에러/버그', 'error', '에러 메시지, 버그, 예외 상황에 대한 질문입니다.'),
    ('개념/이론', 'concept', '개념 이해와 이론 설명이 필요한 질문입니다.'),
    ('구현/코드', 'implementation', '기능 구현, 코드 작성, 로직 구성에 대한 질문입니다.'),
    ('환경설정', 'environment', '설치, 실행 환경, 설정 문제에 대한 질문입니다.'),
    ('기타', 'etc', '다른 유형에 속하지 않는 질문입니다.'),
]

OLD_CATEGORY_SLUGS = ['qna', 'lecture', 'free']


def apply_question_type_categories(apps, schema_editor):
    Category = apps.get_model('pybo', 'Category')
    Question = apps.get_model('pybo', 'Question')

    categories = {}
    for name, slug, description in QUESTION_TYPE_CATEGORIES:
        category, _ = Category.objects.update_or_create(
            slug=slug,
            defaults={'name': name, 'description': description},
        )
        categories[slug] = category

    Question.objects.filter(category__slug__in=OLD_CATEGORY_SLUGS).update(category=categories['etc'])
    Category.objects.filter(slug__in=OLD_CATEGORY_SLUGS).delete()


def revert_question_type_categories(apps, schema_editor):
    Category = apps.get_model('pybo', 'Category')
    Question = apps.get_model('pybo', 'Question')

    qna, _ = Category.objects.update_or_create(
        slug='qna',
        defaults={'name': '질문답변', 'description': '질문과 답변을 나누는 게시판입니다.'},
    )
    Category.objects.update_or_create(
        slug='lecture',
        defaults={'name': '강좌', 'description': '강좌 게시판입니다.'},
    )
    Category.objects.update_or_create(
        slug='free',
        defaults={'name': '자유게시판', 'description': '자유롭게 글을 남기는 게시판입니다.'},
    )

    Question.objects.filter(category__slug__in=[slug for _, slug, _ in QUESTION_TYPE_CATEGORIES]).update(category=qna)
    Category.objects.filter(slug__in=[slug for _, slug, _ in QUESTION_TYPE_CATEGORIES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('pybo', '0012_contentreport_snapshot'),
    ]

    operations = [
        migrations.RunPython(apply_question_type_categories, revert_question_type_categories),
    ]
