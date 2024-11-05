from datetime import timedelta

import pytest
from django.utils import timezone
from news.forms import CommentForm
from news.models import Comment, News

from .constants import NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.usefixtures('db')
class TestHomePage:

    def test_order_and_count_news(self, pages, client, add_news):
        """Тест пагинации и сортировки на главной странице."""
        News.objects.bulk_create(add_news)
        response = client.get(pages['HOME'])
        object_list = response.context['object_list']
        news_count = object_list.count()
        all_dates = [news.date for news in object_list]
        sorted_dates = sorted(all_dates, reverse=True)
        assert news_count == NEWS_COUNT_ON_HOME_PAGE, 'Ошибка пагинации'
        assert all_dates == sorted_dates, 'Ошибка сортировки'


@pytest.mark.usefixtures("db")
class TestDetailPage:

    def test_news_and_form_in_context(self, client, pages, author_client):
        """Тест правильности написания названия объекта в контексте,
        проверка формата передаваемых объектов и проверка на отсутствие формы
        комментирования для неавторизованных пользователей.
        """
        url = pages['DETAIL']
        response = client.get(url)
        assert 'news' in response.context, (
            'Неверное имя новости, передаваемое в контекст.')
        assert isinstance(response.context['news'], News)
        assert 'form' not in response.context, (
            'Отображается форма для анонимного пользователя')
        response = author_client.get(url)
        assert 'form' in response.context, (
            'Отсутвует форма комментария для авторизованного пользователя.')
        assert isinstance(response.context['form'], CommentForm), (
            'Неверный формат передаваемой формы.'
        )

    def test_order_comments(self, client, pages, news, authtor_comment):
        """Тест сортировки комментариев."""
        now = timezone.now()
        for index in range(10):
            comment = Comment.objects.create(
                news=news, author=authtor_comment, text=f'Tекст {index}')
            comment.created = now + timedelta(days=index)
            comment.save()
        url = pages['DETAIL']
        response = client.get(url)
        news = response.context['news']
        all_comments = news.comment_set.all()
        all_timestamps = [comment.created for comment in all_comments]
        sorted_timestamps = sorted(all_timestamps)
        assert all_timestamps == sorted_timestamps, (
            'Неправильная сортировака комментариев, по дате добавления.')
