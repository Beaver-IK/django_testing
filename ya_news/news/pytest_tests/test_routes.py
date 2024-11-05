from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize('name, args', (
    ('users:login', None),
    ('users:logout', None),
    ('users:signup', None),
    ('news:home', None),
    ('news:detail', pytest.lazy_fixture('news_id')),),)
def test_pages_availability(client, name, args):
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'client_user, status_user',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_availability_for_comment_edit_and_delete(client_user, comment_id,
                                                  name, status_user):
    """Тест на проверку редактирования и удаления
    комментария автором и читателем.
    """
    url = reverse(name, args=comment_id)
    response = client_user.get(url)
    assert response.status_code == status_user


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_redirect_for_anonymous_client(client, name, comment_id):
    """Тест на перенаправление неавторизованных пользователей."""
    url = reverse(name, args=comment_id)
    login_url = reverse('users:login')
    response = client.get(url)
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
