from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from ..exceptions import PyboServiceError
from ..services import list_user_bookmarks, toggle_question_bookmark


@login_required(login_url='common:login')
def bookmark_question(request, question_id):
    try:
        result = toggle_question_bookmark(request.user, question_id)
    except PyboServiceError as error:
        messages.error(request, str(error))
        return redirect('pybo:index')

    if result.bookmarked:
        messages.success(request, '북마크에 저장했습니다.')
    else:
        messages.success(request, '북마크를 해제했습니다.')
    return redirect('pybo:detail', question_id=question_id)


@login_required(login_url='common:login')
def bookmark_list(request):
    bookmarks = list_user_bookmarks(request.user)
    return render(request, 'pybo/bookmark_list.html', {'bookmarks': bookmarks})
