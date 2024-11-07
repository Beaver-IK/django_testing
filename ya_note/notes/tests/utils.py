from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class BaseTestCase(TestCase):
    """Базовый набор функций и переменных для тестов."""

    @classmethod
    def setUpTestData(cls):
        cls.AUTHOR = User.objects.create(username='Автор')
        cls.READER = User.objects.create(username='Не автор')
        cls.author_client = Client()
        cls.reader_client = Client()
        cls.author_client.force_login(cls.AUTHOR)
        cls.reader_client.force_login(cls.READER)
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст', author=cls.AUTHOR)
        cls.PAGE = None
        cls.PAGES = dict(
            HOME=reverse('notes:home'),
            LOGIN=reverse('users:login'),
            LOGOUT=reverse('users:logout'),
            SIGNUP=reverse('users:signup'),
            SUCCESS=reverse('notes:success'),
            ADD=reverse('notes:add'),
            DETAIL=reverse(viewname='notes:detail', args=(cls.note.slug,)),
            DELETE=reverse('notes:delete', args=(cls.note.slug,)),
            EDIT=reverse('notes:edit', args=(cls.note.slug,)),
            LIST=reverse('notes:list'))

    def redirect_login_page(self, url):
        return f'{self.PAGES["LOGIN"]}?next={url}'

    def reset_count(self):
        Note.objects.all().delete()
        return Note.objects.count()

    def notes_count(self):
        return Note.objects.count()

    def form_data(self, slug='new_slug'):
        return dict(
            title='Новый заголовок',
            text='Новый текст',
            slug=slug)

    def new_form_data(self, slug='reader_slag'):
        return dict(
            title='Новый заголовок не от владельца',
            text='Новый текст не от владельца',
            slug=slug)
