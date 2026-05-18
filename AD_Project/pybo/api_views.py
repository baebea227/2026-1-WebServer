from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .exceptions import PyboServiceError
from .serializers import BookmarkSerializer, QuestionSerializer, UserSerializer
from .services import (
    BoardSummary,
    RequestMessage,
    list_user_bookmarks,
    login_user,
    logout_user,
    search_questions,
    toggle_question_bookmark,
)


def service_error_response(error):
    return Response(
        {
            'detail': str(error),
            'code': error.code,
        },
        status=error.status_code,
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def request_info(request):
    message = RequestMessage.from_request(request)
    return Response(message.as_dict())


@api_view(['POST'])
@permission_classes([AllowAny])
def auth_login(request):
    try:
        user = login_user(
            request,
            request.data.get('username'),
            request.data.get('password'),
        )
    except PyboServiceError as error:
        return service_error_response(error)
    return Response({'user': UserSerializer(user).data, 'message': '로그인되었습니다.'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def auth_logout(request):
    logout_user(request)
    return Response({'message': '로그아웃되었습니다.'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def auth_me(request):
    return Response({'user': UserSerializer(request.user).data})


@api_view(['GET'])
@permission_classes([AllowAny])
def question_list(request):
    questions = search_questions(
        keyword=request.query_params.get('keyword', ''),
        order=request.query_params.get('order', 'recent'),
    )
    return Response(QuestionSerializer(questions, many=True).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def question_bookmark(request, question_id):
    try:
        result = toggle_question_bookmark(request.user, question_id)
    except PyboServiceError as error:
        return service_error_response(error)
    return Response(result.as_dict())


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def bookmark_list(request):
    try:
        bookmarks = list_user_bookmarks(request.user)
    except PyboServiceError as error:
        return service_error_response(error)
    return Response(BookmarkSerializer(bookmarks, many=True).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def board_summary(request):
    return Response(BoardSummary.from_database().as_dict())
