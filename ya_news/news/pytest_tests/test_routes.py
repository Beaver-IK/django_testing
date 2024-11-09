from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf

pytestmark = pytest.mark.django_db
# Адреса страниц
LOGIN = lf('login_page')
LOGOUT = lf('logout_page')
SIGNUP = lf('signup_page')
HOME = lf('home_page')
DETAIL = lf('detail_page')
EDIT = lf('edit_page')
DELETE = lf('delete_page')
# Клиенты пользователей
CLIENT = lf('client')
AUTHOR_CLIENT = lf('author_client')
READER_CLIENT = lf('reader_client')


@pytest.mark.parametrize(
    'url, client_user,  status', (
        (LOGIN, CLIENT, HTTPStatus.OK,),
        (SIGNUP, CLIENT, HTTPStatus.OK,),
        (LOGOUT, CLIENT, HTTPStatus.OK,),
        (HOME, CLIENT, HTTPStatus.OK,),
        (DETAIL, CLIENT, HTTPStatus.OK,),
        (EDIT, AUTHOR_CLIENT, HTTPStatus.OK,),
        (DELETE, AUTHOR_CLIENT, HTTPStatus.OK,),
        (EDIT, READER_CLIENT, HTTPStatus.NOT_FOUND,),
        (DELETE, READER_CLIENT, HTTPStatus.NOT_FOUND,),),)
def test_pages_availability(url, client_user, status):
    response = client_user.get(url)
    assert response.status_code == status


@pytest.mark.parametrize(
    'name', (
        EDIT,
        DELETE,),)
def test_availability_for_comment_edit_and_delete(client, login_page, name):
    """Тест перенаправления незалогинененного пользователя,
    при попытке редактирования или удаления комментария.
    """
    response = client.get(name)
    expected_url = f'{login_page}?next={name}'
    assertRedirects(response, expected_url)
