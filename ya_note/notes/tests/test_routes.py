from http import HTTPStatus

from notes.tests.utils import BaseData


class TestRoutes(BaseData):
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
        """Тест доступности страниц детализации, редактирования
        и удаления заметки для других пользователей.
        """
        users = (
            (self.AUTHOR),
            (self.READER),
        )
        urls = (
            self.PAGES['EDIT'],
            self.PAGES['DELETE'],
            self.PAGES['DETAIL'],
            self.PAGES['ADD'],
            self.PAGES['SUCCESS'],
            self.PAGES['LIST']
        )
        for user in users:
            for name in urls:
                with self.subTest(user=user, name=name):
                    if user == self.AUTHOR:
                        response = self.author_client.get(name)
                        self.assertEqual(
                            response.status_code, HTTPStatus.OK,
                            msg=f'{user} не смог зайти на страницу {name}')
                    else:
                        response = self.client.get(name)
                        self.assertEqual(
                            response.status_code, HTTPStatus.FOUND,
                            msg=f'Не автор смог зайти на страницу {name}')

    def test_redirect_for_anonymus(self):
        """Тест редиректа анонимного пользователя на страницу авторизации."""
        urls = (
            self.PAGES['EDIT'],
            self.PAGES['DELETE'],
            self.PAGES['DETAIL'],
            self.PAGES['ADD'],
            self.PAGES['SUCCESS'],
            self.PAGES['LIST']
        )
        for name in urls:
            with self.subTest(name=name):
                url = name
                redirect_url = self.redirect_login_page(name)
                response = self.client.get(url)
                self.assertRedirects(
                    response, redirect_url,
                    msg_prefix=f'Аноним небыл перенаправлен на {redirect_url}')
