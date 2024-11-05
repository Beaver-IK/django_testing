from notes.forms import NoteForm
from notes.models import Note
from tests.utils import BaseData


class TestAddNotePage(BaseData):
    """Кейс проверки контента страницы создания заметки."""

    def setUp(self):
        self.PAGE = self.PAGES['ADD']

    def test_tranfer_form(self):
        """Тест на передачу формы и ее соответствие формату."""
        response = self.author_client.get(self.PAGE)
        self.assertIn(
            'form', response.context,
            msg=(f'Форма "form" не была передана в словарь '
                 f'контекста страницы {self.PAGE}'))
        self.assertIsInstance(
            response.context['form'], NoteForm,
            msg='Формат формы не соответсвует NoteForm')


class TestEditNotePage(TestAddNotePage):
    """Кейс проверки контента страницы редактирования заметки."""

    def setUp(self):
        self.PAGE = self.PAGES['EDIT']


class TestDetailPage(BaseData):
    """Кейс проверки контента страницы заметки."""

    def setUp(self):
        self.PAGE = self.PAGES['DETAIL']

    def test_transfer_note(self):
        """Тест на передачу объекта нужного формата под ожидаемым именем."""
        response = self.author_client.get(self.PAGE)
        self.assertIn(
            'note', response.context,
            msg=(f'Объект "note" не была передана в словарь '
                 f'контекста страницы {self.PAGE}'))
        self.assertIsInstance(
            response.context['note'], Note,
            msg='Объект "note" не является объектом Note')


class TestDeletePage(TestDetailPage):
    """Кейс проверки страницы удаления заметки."""

    def setUp(self):
        self.PAGE = self.PAGES['DELETE']


class TestNotesListPage(BaseData):
    """Кейс проверки страницы списка заметок."""

    def setUp(self):
        self.PAGE = self.PAGES['LIST']

    def test_note_order(self):
        """Тест на сортировку заметок от старых к новым."""
        Note.objects.create(
            title='Новый заголовок', text='Новый текст', author=self.AUTHOR)
        response = self.author_client.get(self.PAGE)
        note_list = response.context['object_list']
        all_id = [note.id for note in note_list]
        sorted_id = sorted(all_id)
        self.assertEqual(
            all_id, sorted_id,
            msg=f'Неправильная сортировка на странице {self.PAGE}')

    def test_only_author_notes(self):
        """Тест на отображение только авторских заметок и на
        попытку получить доступ к странице неавтора заметок.
        """
        for user, content in (
            (self.author_client, True), (self.reader_client, False)
        ):
            with self.subTest(user=user):
                self.assertEqual(
                    self.note in user.get(self.PAGE)
                    .context['object_list'], content,
                    msg='Читатель может просматривать список чужих заметок')
