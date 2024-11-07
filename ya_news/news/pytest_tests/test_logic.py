import pytest

from http import HTTPStatus

from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

FORM_DATA = {'text': 'Текст комментария'}
NEW_FORM_DATA = {'text': 'Новый текст комментария'}


@pytest.mark.usefixtures('db')
class TestCommentCreate:
    """Кейс создания комментариев."""

    def test_create_comment(self, news, client, authtor_comment,
                            author_client, detail_page):
        """Тест на добавление комментария зарегистрированным
        и анонимным пользователем. Проверка перенаправления на страницу
        добавления комментария.
        """
        url = detail_page
        count_comments = Comment.objects.count()
        client.post(url, data=FORM_DATA)
        assert Comment.objects.count() == count_comments, (
            'Анонимный пользователь смог добавить комментарий.')
        response = author_client.post(url, data=FORM_DATA)
        assert Comment.objects.count() == count_comments + 1, (
            'Авторизованный пользователь не смог оставить комментарий.')
        new_comment = Comment.objects.all().last()
        assert new_comment.text == FORM_DATA['text'], (
            'Текст добавленного комментария отличается от ожидаемого.')
        assert new_comment.author == authtor_comment, (
            'Автор комментария отличается от ожидаемого.')
        assert new_comment.news == news, (
            'Новость к котрой относится комментарий была изменена.')
        assertRedirects(response, f'{detail_page}#comments',
                        msg_prefix=('Неудачная попытка перенаправления '
                                    'после добавления комментария.'))

    def test_user_cant_use_bad_words(self, author_client, detail_page):
        """Тест на использование запрещенных слов."""
        url = detail_page
        bad_words = dict(
            text=f'Текст, {BAD_WORDS[0]}, тут тоже текст'
        )
        comment_count = Comment.objects.count()
        response = author_client.post(url, data=bad_words)
        assertFormError(
            response=response,
            form='form',
            field='text',
            errors=WARNING,
            msg_prefix=('Был создан комментарий с '
                        'использованием запрещенных слов'))
        assert comment_count == Comment.objects.count()


@pytest.mark.usefixtures('db')
class TestEditDeleteComment:
    """Кейс для тестирования функций
    удаления и редактирования комментариев.
    """

    def test_edit_comment(self, client, reader_client,
                          comment, author_client, edit_page,
                          login_page, detail_page):
        """Тест функционала редактирования комментария."""
        url = edit_page
        comment = Comment.objects.get()
        response = client.post(url, NEW_FORM_DATA)
        assertRedirects(
            response, f'{login_page}?next={url}',
            msg_prefix='Неавторизованный пользователь '
            'небыл перенаправлен на страницу авторизации.')
        response = reader_client.post(url, NEW_FORM_DATA)
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            'Не автор смог отправить запрос на изменение комментария.')
        comment.refresh_from_db()
        assert comment.text != NEW_FORM_DATA['text'], (
            'Комментарий был изменен не автором.')
        response = author_client.post(url, NEW_FORM_DATA)
        assertRedirects(response, f'{detail_page}#comments')
        comment.refresh_from_db()
        assert comment.text == NEW_FORM_DATA['text'], (
            'Комментарий небыл изменен автором.')

    def test_delete_comment(self, reader_client, author_client,
                            delete_page, detail_page):
        """Тест функционала удаления комментария."""
        url = delete_page
        count_comments = Comment.objects.count()
        response = reader_client.delete(url)
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            'Не автор смог отправить запрос на удаление комментария.')
        assert Comment.objects.count() == count_comments, (
            'Не автор, смог удалить комментарий')
        response = author_client.delete(url)
        assertRedirects(
            response, f'{detail_page}#comments',
            msg_prefix='После удаления комментария, '
            'автор небыл перенаправлен на страницу новости.')
        assert Comment.objects.count() == count_comments - 1, (
            'Комментарий небыл удален из БД.')
