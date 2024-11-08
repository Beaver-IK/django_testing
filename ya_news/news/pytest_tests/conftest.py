from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News

COMMENTS_COUNT = 10


def generate_news():
    today = datetime.today()
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        yield News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index))


@pytest.fixture
def news():
    """Создает и возвращает объект новости"""
    return News.objects.create(
        title='Заголовок новсти.',
        text='Новостной текст.'
    )


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
def add_news():
    """Возвращает список новостей согласно установленной пагинации."""
    News.objects.bulk_create(generate_news())


@pytest.fixture
def add_comments(news, authtor_comment):
    now = timezone.now()
    for index in range(COMMENTS_COUNT):
        comment = Comment.objects.create(news=news, author=authtor_comment,
                                         text=f'Tекст {index}')
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture()
def enable_db_access(db):
    """Автоматически включает доступ к базе данных для всех тестов."""


@pytest.fixture
def home_page():
    """Возвращает адрес домашней страницы."""
    return reverse('news:home')


@pytest.fixture
def delete_page(comment):
    """Возвращает страницу удаления комментария."""
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def edit_page(comment):
    """Возвращает страницу редактирования комментария."""
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def detail_page(news):
    """Возращает страницу новости."""
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def login_page():
    """Возвращает страницу авторизации."""
    return reverse('users:login')


@pytest.fixture
def logout_page():
    """Возвращает страницу выхода из аккаунта."""
    return reverse('users:logout')


@pytest.fixture
def signup_page():
    """Возвращает страницу подстверждения."""
    return reverse('users:signup')
