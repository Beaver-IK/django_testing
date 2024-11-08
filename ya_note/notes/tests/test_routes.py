from http import HTTPStatus

from notes.tests.utils import BaseTestCase


class TestRoutes(BaseTestCase):
    """Кейс тестирования маршрутизатора."""

    def test_response_status(self):
        """Тест проверки статус кодов."""
        access = (
            (self.PAGES['HOME'], self.client, HTTPStatus.OK),
            (self.PAGES['LOGIN'], self.client, HTTPStatus.OK),
            (self.PAGES['LOGOUT'], self.client, HTTPStatus.OK),
            (self.PAGES['SIGNUP'], self.client, HTTPStatus.OK),
            (self.PAGES['LIST'], self.reader_client, HTTPStatus.OK),
            (self.PAGES['SUCCESS'], self.reader_client, HTTPStatus.OK),
            (self.PAGES['ADD'], self.reader_client, HTTPStatus.OK),
            (self.PAGES['DETAIL'], self.author_client, HTTPStatus.OK),
            (self.PAGES['DELETE'], self.author_client, HTTPStatus.OK),
            (self.PAGES['EDIT'], self.author_client, HTTPStatus.OK),
            (self.PAGES['DETAIL'], self.reader_client, HTTPStatus.NOT_FOUND),
            (self.PAGES['DELETE'], self.reader_client, HTTPStatus.NOT_FOUND),
            (self.PAGES['EDIT'], self.reader_client, HTTPStatus.NOT_FOUND),
        )
        for url, client, status in access:
            with self.subTest(name=url, client=client, status=status):
                response = client.get(url)
                self.assertEqual(
                    response.status_code, status,
                    msg='Ошибка доступа')

    def test_redirects(self):
        """Тест перенаправления."""
        urls = (
            self.PAGES['LIST'],
            self.PAGES['SUCCESS'],
            self.PAGES['ADD'],
            self.PAGES['DETAIL'],
            self.PAGES['EDIT'],
            self.PAGES['DELETE'],
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                redirect_url = self.redirect_login_page(url)
                self.assertRedirects(response, redirect_url)
