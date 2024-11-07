import pytest

from http import HTTPStatus

from pytest_django.asserts import assertRedirects

from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name', (
        (pytest.lazy_fixture('login_page')),
        (pytest.lazy_fixture('logout_page')),
        (pytest.lazy_fixture('signup_page')),
        (pytest.lazy_fixture('home_page')),
        (pytest.lazy_fixture('detail_page')),),)
def test_pages_availability(client, name):
    response = client.get(name)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'client_user, status_user',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND)
    ),
)
@pytest.mark.parametrize(
    'name', (
        (pytest.lazy_fixture('edit_page')),
        (pytest.lazy_fixture('delete_page')),),)
def test_availability_for_comment_edit_and_delete(client_user, comment,
                                                  name, status_user):
    """Тест на проверку редактирования и удаления
    комментария автором и читателем.
    """
    response = client_user.get(name)
    assert response.status_code == status_user


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name', (
        (pytest.lazy_fixture('edit_page')),
        (pytest.lazy_fixture('delete_page')),),)
def test_redirect_for_anonymous_client(client, name):
    """Тест на перенаправление неавторизованных пользователей."""
    url = name
    login_url = reverse('users:login')
    response = client.get(url)
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
