from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post

User = get_user_model()


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()
        cls.user = User.objects.create_user(username='testuser')
        cls.group = Group.objects.create(
            title='testtitle',
            slug='testgroup',
            description='testdescription',
        )
        cls.post = Post.objects.create(
            text='testtext',
            author=cls.user,
            group=cls.group,
        )
        cls.form_data = {
            'text': cls.post.text,
            'group': cls.group.id,
        }

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTest.user)
        self.guest_client = Client()

    def test_create_post(self):
        post_count = Post.objects.count()
        context = {
            'text': 'testtext',
            'group': PostFormTest.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=context,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile',
                             args=[self.user.username]))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=context['text'],
                group=self.group,
                author=self.user
            ).exists()
        )

    def test_edit_post(self):
        post_count = Post.objects.count()
        context = {
            'text': 'changepost',
            'group': ''
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={
                'post_id': PostFormTest.post.id}),
            data=context,
            follow=True
        )
        PostFormTest.post.refresh_from_db()
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': PostFormTest.post.id}))
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(PostFormTest.post.text, context['text'])
        self.assertEqual(PostFormTest.post.group, None)

    def test_no_user_create_post(self):
        post_count = Post.objects.count()
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=PostFormTest.form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count)
        self.assertRedirects(response,
                             reverse('users:login') + '?next=' + reverse(
                                 'posts:post_create'))
        self.assertEqual(Post.objects.count(), post_count)

    def test_no_user_edit_post(self):
        context = {
            'text': 'trychangepost',
            'group': ''
        }
        response = self.client.post(
            reverse('posts:post_edit', kwargs={
                'post_id': PostFormTest.post.id}),
            data=context,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'users:login') + '?next=' + reverse(
                'posts:post_edit', kwargs={'post_id': PostFormTest.post.id}))
        self.assertNotEqual(PostFormTest.post.text, context['text'])
