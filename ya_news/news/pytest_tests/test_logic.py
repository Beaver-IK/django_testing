from http import HTTPStatus

import pytest
from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from pytest_django.asserts import assertFormError, assertRedirects


@pytest.mark.usefixtures('db')
class TestCommentCreate:
    """Кейс создания комментариев."""

    def test_create_comment(self, news, pages, client, authtor_comment,
                            author_client, form_data):
        """Тест на добавление комментария зарегистрированным
        и анонимным пользователем. Проверка перенаправления на страницу
        добавления комментария.
        """
        url = pages['DETAIL']
        count_comments = Comment.objects.count()
        client.post(url, data=form_data)
        assert Comment.objects.count() == count_comments, (
            'Анонимный пользователь смог добавить комментарий.')
        response = author_client.post(url, data=form_data)
        assert Comment.objects.count() == count_comments + 1, (
            'Авторизованный пользователь не смог оставить комментарий.')
        new_comment = Comment.objects.all().last()
        assert new_comment.text == form_data['text'], (
            'Текст добавленного комментария отличается от ожидаемого.')
        assert new_comment.author == authtor_comment, (
            'Автор комментария отличается от ожидаемого.')
        assert new_comment.news == news, (
            'Новость к котрой относится комментарий была изменена.')
        assertRedirects(response, f'{pages["DETAIL"]}#comments',
                        msg_prefix=('Неудачная попытка перенаправления '
                                    'после добавления комментария.'))

    def test_user_cant_use_bad_words(self, pages, author_client):
        """Тест на использование запрещенных слов."""
        url = pages['DETAIL']
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

    def test_edit_comment(self, new_form_data, client, reader_client,
                          comment, author_client, pages):
        """Тест функционала редактирования комментария."""
        url = pages['EDIT']
        comment = Comment.objects.get()
        response = client.post(url, new_form_data)
        assertRedirects(
            response, f'{pages["LOGIN"]}?next={url}',
            msg_prefix='Неавторизованный пользователь '
            'небыл перенаправлен на страницу авторизации.')
        response = reader_client.post(url, new_form_data)
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            'Не автор смог отправить запрос на изменение комментария.')
        comment.refresh_from_db()
        assert comment.text != new_form_data['text'], (
            'Комментарий был изменен не автором.')
        response = author_client.post(url, new_form_data)
        assertRedirects(response, f'{pages["DETAIL"]}#comments')
        comment.refresh_from_db()
        assert comment.text == new_form_data['text'], (
            'Комментарий небыл изменен автором.')

    def test_delete_comment(self, reader_client, author_client, pages):
        """Тест функционала удаления комментария."""
        url = pages['DELETE']
        count_comments = Comment.objects.count()
        response = reader_client.delete(url)
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            'Не автор смог отправить запрос на удаление комментария.')
        assert Comment.objects.count() == count_comments, (
            'Не автор, смог удалить комментарий')
        response = author_client.delete(url)
        assertRedirects(
            response, f'{pages["DETAIL"]}#comments',
            msg_prefix='После удаления комментария, '
            'автор небыл перенаправлен на страницу новости.')
        assert Comment.objects.count() == count_comments - 1, (
            'Комментарий небыл удален из БД.')
