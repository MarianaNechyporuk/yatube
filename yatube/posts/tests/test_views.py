from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post
from yatube import settings

User = get_user_model()


class TaskPagesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='text',
            slug='123',
        )
        self.post = Post.objects.create(
            text='testtext',
            author=self.user,
            group=self.group
        )
        self.form_data = {
            'text': self.post.text,
            'group': self.group.id,
        }
        self.new_post = self.authorized_client.post(
            reverse('posts:post_create'),
            data=self.form_data,
            follow=True
        )
        self.public_index_template = 'posts/index.html'
        self.public_group_page_template = 'posts/group_list.html'
        self.private_create_post_template = 'posts/create_post.html'
        self.private_edit_post_template = 'posts/create_post.html'
        self.public_profile = 'posts/profile.html'
        self.public_post = 'posts/post_detail.html'

    def test_pages_show_correct_template(self):
        templates_pages_names = {
            self.public_index_template: reverse('posts:index'),
            self.public_profile: reverse('posts:profile',
                                         kwargs={'username': self.user}),
            self.public_post: reverse('posts:post_detail',
                                      kwargs={'post_id': self.post.id}),
            self.private_edit_post_template: reverse('posts:post_edit',
                                                     kwargs={'post_id':
                                                             self.post.id}),
            self.private_create_post_template: reverse('posts:post_create'),
            self.public_group_page_template: (
                reverse('posts:group_posts', kwargs={'slug': self.group.slug})
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_context(self):
        url_names = [reverse('posts:index'),
                     reverse('posts:post_detail',
                             kwargs={'post_id': self.post.id}),
                     reverse('posts:post_edit',
                             kwargs={'post_id': self.post.id}),
                     reverse('posts:group_posts',
                             kwargs={'slug': self.group.slug}),
                     reverse('posts:profile',
                             kwargs={'username': self.user.username})]
        for url in url_names:
            response = self.authorized_client.get(url)
            self.assertContains(response, self.form_data['text'])
            self.assertContains(response, self.user)
            self.assertContains(response, self.group.id)
            self.assertContains(response, self.post.id)

    def test_check_post_in_group(self):
        t_group = Group.objects.create(
            title='sometitle',
            slug='test',
            description='sometext',
        )
        Group.objects.create(
            title='sometitle1',
            slug='test1',
            description='sometext1',
        )
        Post.objects.create(
            text='testtext',
            author=self.user,
            group=t_group,
        )
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}))
        self.assertEqual(response.context['group'].title, self.group.title)
        self.assertEqual(response.context['group'].slug, self.group.slug)
        self.assertEqual(response.context['group'].description,
                         self.group.description)
        first_object = response.context['page_obj'][0]
        post_text = first_object.text
        post_group = first_object.group
        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post_group.title, self.group.title)
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': self.group.slug})
        )
        self.assertFalse(response.context['page_obj'].has_next())

    def test_chech_show_post_in_index_and_profile(self):
        templates_pages_names = {reverse('posts:index'),
                                 reverse('posts:profile',
                                 kwargs={'username': self.user.username})}
        for reverse_name in templates_pages_names:
            response = self.authorized_client.get(
                reverse_name)
            first_object = response.context['page_obj'][0]
            post_text = first_object.text
            self.assertEqual(post_text, self.post.text)
            first_object = response.context['page_obj'][0]
            post_text = first_object.text
            self.assertFalse(response.context['page_obj'].has_next())


class PaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testuser')
        cls.group = Group.objects.create(
            title='testtitle',
            slug='testslug',
            description='testdescription',
        )
        cls.post = settings.PAGE_NUM + 3
        for cls.post in range(settings.PAGE_NUM + 3):
            cls.post = Post.objects.create(
                text='testtext',
                author=cls.user,
                group=cls.group
            )

    def test_first_page_show_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']),
                         settings.PAGE_NUM)

    def test_second_page_show_three_records(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_first_page_show_ten_records(self):
        response = self.client.get(reverse(
            'posts:group_posts', kwargs={
                'slug': PaginatorTests.group.slug
            })
        )
        self.assertEqual(len(response.context['page_obj']),
                         settings.PAGE_NUM)

    def test_group_second_page_show_three_records(self):
        response = self.client.get(reverse(
            'posts:group_posts', kwargs={
                'slug': PaginatorTests.group.slug
            }) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_profile_first_page_show_ten_records(self):
        response = self.client.get(reverse(
            'posts:profile', kwargs={
                'username': PaginatorTests.user.username,
            })
        )
        self.assertEqual(len(response.context['page_obj']),
                         settings.PAGE_NUM)

    def test_profile_second_page_show_three_records(self):
        response = self.client.get(reverse(
            'posts:profile', kwargs={
                'username': PaginatorTests.user.username,
            }) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)
