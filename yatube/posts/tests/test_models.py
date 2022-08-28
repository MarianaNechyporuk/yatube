from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="testuser")
        cls.group = Group.objects.create(
            title="заголовок поста",
            slug="testslug",
            description="Описание поста",
        )
        cls.post = Post.objects.create(
            group=cls.group, author=cls.user, text="Тестовый текст"
        )

    def test_models_show_correct_names(self):
        group = PostModelTest.group
        expected_title = group.title
        self.assertEqual(expected_title, str(group))
        post = PostModelTest.post
        expected_object_name = post.text[:50]
        self.assertEqual(expected_object_name, str(post))

    def test_verbose_name(self):
        post = PostModelTest.post
        field_verboses = {
            "text": "Текст сообщения",
            "author": "Автор",
            "group": "Группа",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value
                )

    def test_help_texts(self):
        post = PostModelTest.post
        field_help_texts = {
            "author": "Выберите имя автора",
            "group": "Выберите название группы",
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(post._meta.get_field(value).help_text,
                                 expected)
