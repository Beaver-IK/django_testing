from datetime import datetime, timedelta

import pytest
from django.test.client import Client
from django.urls import reverse
from news.models import Comment, News

from .constants import NEWS_COUNT_ON_HOME_PAGE


@pytest.fixture
def news():
    """Создает и возвращает объект новости"""
    news = News.objects.create(
        title='Заголовок новсти.',
        text='Новостной текст.'
    )
    return news


@pytest.fixture
def news_id(news):
    """Возвращает id новости"""
    return (news.id,)


@pytest.fixture
def comment(news, authtor_comment):
    comment = Comment.objects.create(
        news=news,
        author=authtor_comment,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def authtor_comment(django_user_model):
    """Возвращает пользователя автора."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def no_authtor_comment(django_user_model):
    """Возвращает пользователя читателя."""
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def comment_id(comment):
    """Возвращает ID комментария."""
    return (comment.id,)


@pytest.fixture
def author_client(authtor_comment):
    """Возращает клиент автора."""
    client = Client()
    client.force_login(authtor_comment)
    return client


@pytest.fixture
def reader_client(no_authtor_comment):
    """Возвращает клиент читателя."""
    client = Client()
    client.force_login(no_authtor_comment)
    return client


@pytest.fixture
def enable_db_access(db):
    """Включает доступ к базе данных."""


@pytest.fixture
def add_news():
    """Возвращает список новостей согласно установленной пагинации."""
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index))
        for index in range(NEWS_COUNT_ON_HOME_PAGE + 1)]
    return all_news


@pytest.fixture()
def enable_db_access(db):
    """Автоматически включает доступ к базе данных для всех тестов."""


@pytest.fixture
def form_data(news, authtor_comment):
    """Возвращает данные, для создания комментария"""
    return dict(
        text='Текст комментария'
    )


@pytest.fixture
def new_form_data():
    return dict(
        text='Новый текст комментария'
    )


@pytest.fixture
def pages(news_id, comment_id):
    """Возвращает словарь со страницами приложения."""
    return dict(
        HOME=reverse('news:home'),
        DELETE=reverse('news:delete', args=comment_id),
        EDIT=reverse('news:edit', args=comment_id),
        DETAIL=reverse('news:detail', args=news_id),
        LOGIN=reverse('users:login')
    )
