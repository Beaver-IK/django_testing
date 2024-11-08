from http import HTTPStatus

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from notes.tests.utils import BaseTestCase


class TestAddNote(BaseTestCase):
    """Кейс для проверки добавления новой заметки."""

    def setUp(self):
        self.PAGE = self.PAGES['ADD']

    def test_create_note(self):
        """Тест возможности создания заметки
        только залогиненным пользователем.
        """
        count = self.reset_count()
        data = self.form_data()
        response = self.author_client.post(self.PAGE, data=data)
        anon_response = self.client.post(self.PAGE, data=data)
        self.assertRedirects(
            response, self.PAGES['SUCCESS'],
            msg_prefix=f'Нет перенаправлеия на {self.PAGES["SUCCESS"]}')
        self.assertEqual(
            Note.objects.count(), count + 1,
            msg='Новая заметка не создана.')
        note = Note.objects.get()
        self.assertEqual(
            note.title, self.form_data()['title'],
            msg='Заголовок созданный не соответвует заданному')
        self.assertEqual(
            note.text, self.form_data()['text'],
            msg='Текст созданный не соответвует заданному')
        self.assertEqual(
            note.slug, self.form_data()['slug'],
            msg='Slug созданный не соответвует заданному')
        self.assertEqual(
            note.author, self.AUTHOR,
            msg='Автор созданной заметки не соответствует заданному')
        self.assertRedirects(
            anon_response,
            self.redirect_login_page(self.PAGE),
            msg_prefix='Нет перенаправлеия на страницу авторизации')
        self.assertEqual(
            Note.objects.count(), count + 1,
            msg='Незарегистрированный пользователь смог создать заметку')

    def test_slug(self):
        """Тест на указание уникального Slug
        и на автоматическое подтягивание slug из заголовка.
        """
        notes_count = self.notes_count()
        response = self.author_client.post(
            self.PAGE, data=self.form_data(slug=self.note.slug))
        self.assertEqual(
            Note.objects.count(), notes_count,
            msg='Была создана заметка с ранее созданным Slug')
        self.assertFormError(
            response, 'form', 'slug',
            errors=(self.note.slug + WARNING),
            msg_prefix=('Подсказка валидации формы отсутствует'
                        'или указана неверно.'))
        response = self.author_client.post(
            self.PAGE, data=self.form_data(slug='')
        )
        self.assertRedirects(
            response, self.PAGES['SUCCESS'],
            msg_prefix=(
                f'После отправки заметки с пустым Slug'
                f'не переходит перенаправление на {self.PAGES["SUCCESS"]}'))
        self.assertEqual(
            Note.objects.count(), notes_count + 1,
            msg='Не создается объект в БД с указанием пустого Slug')
        no_slug_note = Note.objects.get(pk=2)
        self.assertEqual(
            no_slug_note.slug, slugify(self.form_data()['title']),
            msg=('Slug созданной без указания slug заметки '
                 'не соответствует формату'))


class TestEditNote(BaseTestCase):

    def setUp(self):
        self.PAGE = self.PAGES['EDIT']

    def test_edit_note(self):
        """Тест на редактирование заметки только автором."""
        response_author = self.author_client.post(
            self.PAGE,
            self.form_data()
        )
        response_reader = self.reader_client.post(
            self.PAGE,
            self.new_form_data()
        )
        self.assertRedirects(
            response_author, self.PAGES['SUCCESS'],
            msg_prefix='Автор не смог отредактировать заметку.')
        self.assertEqual(
            response_reader.status_code, HTTPStatus.NOT_FOUND,
            msg='Не автор смог отредактировать заметку.')
        note = Note.objects.get()
        self.assertEqual(
            note.title, self.form_data()['title'],
            msg='Заголовок был изменен не автором заметки.')
        self.assertEqual(
            note.text, self.form_data()['text'],
            msg='Текст был изменен не автором заметки')
        self.assertEqual(
            note.slug, self.form_data()['slug'],
            msg='Slug был изменен не автором')
        self.assertEqual(
            note.author, self.AUTHOR,
            msg='Авторство было изменено')


class TestDeleteNote(BaseTestCase):

    def setUp(self):
        self.PAGE = self.PAGES['DELETE']

    def test_delete_note(self):
        count = self.notes_count()
        response_reader = self.reader_client.post(self.PAGE)
        self.assertEqual(
            response_reader.status_code, HTTPStatus.NOT_FOUND,
            msg='Не автор смог удалить заметку.')
        self.assertEqual(
            Note.objects.count(), count,
            msg='Заметка удаляется не автором.')
        response_author = self.author_client.post(self.PAGE)
        self.assertRedirects(
            response_author, self.PAGES['SUCCESS'],
            msg_prefix=('Автор не был перенаправлен на страницу'
                        'подтверждения удаления'))
        self.assertEqual(
            Note.objects.count(), count - 1,
            msg='Заметка не была удалена и осталась в БД')
