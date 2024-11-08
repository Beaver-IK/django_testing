from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf

pytestmark = pytest.mark.django_db

LOGIN = lf('login_page')
LOGOUT = lf('logout_page')
SIGNUP = lf('signup_page')
HOME = lf('home_page')
DETAIL = lf('detail_page')
EDIT = lf('edit_page')
DELETE = lf('delete_page')


@pytest.mark.parametrize(
    'name', (
        LOGIN,
        LOGOUT,
        SIGNUP,
        HOME,
        DETAIL,),)
def test_pages_availability(client, name):
    response = client.get(name)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'client_user, status_user',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('client'), HTTPStatus.FOUND),
    ),
)
@pytest.mark.parametrize(
    'name', (
        EDIT,
        DELETE,),)
def test_availability_for_comment_edit_and_delete(client_user, login_page,
                                                  name, status_user):
    """Тест на проверку редактирования и удаления
    комментария автором, читателем и анонимом.
    """
    response = client_user.get(name)
    expected_url = f'{login_page}?next={name}'
    assert response.status_code == status_user
    if response.status_code == HTTPStatus.FOUND:
        assertRedirects(response, expected_url)
