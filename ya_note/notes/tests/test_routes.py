from http import HTTPStatus

from notes.tests.utils import BaseTestCase


class TestRoutes(BaseTestCase):
    """Кейс тестирования маршрутизатора."""

    def test_pages_for_everyone(self):
        """Тест доступности страниц для неавторизованных пользователей."""
        urls = (
            self.PAGES['LOGIN'],
            self.PAGES['LOGOUT'],
            self.PAGES['SIGNUP'],
            self.PAGES['HOME'],
        )
        for name in urls:
            with self.subTest(name=name):
                response = self.client.get(name)
                self.assertEqual(
                    response.status_code, HTTPStatus.OK,
                    msg=(f'Страница {name} не доступна '
                         f'для неавторизованного пользователя'))

    def test_availability_for_notes_edit_delete(self):
        """Тест доступности и перенаправления страниц детализации,
        редактирования и удаления заметки для других пользователей и анониимов.
        """
        users = (
            (self.AUTHOR.username, self.author_client, HTTPStatus.OK),
            (self.READER.username, self.reader_client, HTTPStatus.NOT_FOUND),
            ('Аноним', self.client, HTTPStatus.FOUND),
        )
        urls = (
            self.PAGES['EDIT'],
            self.PAGES['DELETE'],
            self.PAGES['DETAIL'],
        )
        for user, client, status in users:
            for name in urls:
                with self.subTest(user=user, name=name, status=status):
                    response = client.get(name)
                    self.assertEqual(response.status_code, status)
                    if status == HTTPStatus.FOUND:
                        redirect_url = self.redirect_login_page(name)
                        self.assertRedirects(response, redirect_url,
                                             msg_prefix=(
                                                 f'Аноним небыл перенаправлен '
                                                 f'на {redirect_url}'))

    def test_availability_for_add_and_list_notes(self):
        """Тест доступности и перенаправления страниц добавления заметок
        и списка заметок для зарегистрированного пользователя и анонима.
        """
        users = (
            (self.AUTHOR.username, self.author_client, HTTPStatus.OK),
            ('Аноним', self.client, HTTPStatus.FOUND),
        )
        urls = (
            self.PAGES['ADD'],
            self.PAGES['SUCCESS'],
            self.PAGES['LIST']
        )
        for user, client, status in users:
            for name in urls:
                with self.subTest(user=user, name=name, status=status):
                    response = client.get(name)
                    self.assertEqual(response.status_code, status)
                    if status == HTTPStatus.FOUND:
                        redirect_url = self.redirect_login_page(name)
                        self.assertRedirects(response, redirect_url,
                                             msg_prefix=(
                                                 f'Аноним небыл перенаправлен '
                                                 f'на {redirect_url}'))
