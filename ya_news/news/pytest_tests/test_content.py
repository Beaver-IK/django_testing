import pytest
from django.conf import settings

from news.forms import CommentForm
from news.models import News

pytestmark = pytest.mark.django_db


class TestHomePage:

    def test_order_and_count_news(self, home_page, client, add_news):
        """Тест пагинации и сортировки на главной странице."""
        response = client.get(home_page)
        object_list = response.context['object_list']
        news_count = object_list.count()
        all_dates = [news.date for news in object_list]
        sorted_dates = sorted(all_dates, reverse=True)
        assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE, (
            'Ошибка пагинации')
        assert all_dates == sorted_dates, 'Ошибка сортировки'


class TestDetailPage:

    def test_news_and_form_in_context_for_anonim(self, client, detail_page):
        """Тест корректного названия объекта в контексте, проверка на
        отсутствие формы комментирования для неавторизованных пользователей.
        """
        url = detail_page
        response = client.get(url)
        assert 'news' in response.context, (
            'Неверное имя новости, передаваемое в контекст.')
        assert isinstance(response.context['news'], News)
        assert 'form' not in response.context, (
            'Отображается форма для анонимного пользователя')

    def test_form_in_context_for_auth_user(self, author_client, detail_page):
        """Тест наличия и соответвия формата формы для"""
        url = detail_page
        response = author_client.get(url)
        assert isinstance(response.context.get('form'), CommentForm), (
            'Неверный формат передаваемой формы.'
        )

    def test_order_comments(self, client, news, detail_page, add_comments):
        """Тест сортировки комментариев."""
        url = detail_page
        response = client.get(url)
        news = response.context['news']
        all_comments = news.comment_set.all()
        all_timestamps = [comment.created for comment in all_comments]
        sorted_timestamps = sorted(all_timestamps)
        assert all_timestamps == sorted_timestamps, (
            'Неправильная сортировака комментариев, по дате добавления.')
