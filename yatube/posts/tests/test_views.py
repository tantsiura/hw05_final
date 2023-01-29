from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Comment, Follow, Group, Post

User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Test')
        posts_list = []
        for i in range(0, settings.ITEMS_FOR_TEST):
            new_post = Post(
                author=cls.user,
                text=f'Тестовый пост {i}',
            )
            posts_list.append(new_post)
        cls.post = Post.objects.bulk_create(posts_list)
        cache.clear()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        cache.clear()
        self.assertEqual(
            len(response.context['page_obj']),
            settings.ITEMS_PER_PAGE
        )

    def test_second_page_contains_three_records(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(
            response.context['page_obj']),
            settings.ITEMS_FOR_TEST - settings.ITEMS_PER_PAGE)


class CommentViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Test3')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_comment_on_the_correct_pages(self):
        ''' После успешной отправки
        комментарий появляется на странице поста.
        '''
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.post.author,
            text='Тестовый комментарий',
        )
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}))
        first_object = response.context['comments'][0]
        self.assertEqual(self.comment.text, first_object.text)


class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Test')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Category_1',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(PostsViewsTests.post.author)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': f'{PostsViewsTests.user.username}'}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{PostsViewsTests.post.pk}'}
            ),
            'posts/create_post.html': (
                reverse('posts:post_create')
            )
        }
        cache.clear()
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
        cache.clear()

    def test_post_edit_by_author_uses_correct_template(self):
        """
        Проверка шаблона редактирования поста автором posts/create_post.html
        """
        response = self.author_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': f'{PostsViewsTests.post.pk}'}
            )
        )
        self.assertTemplateUsed(response, 'posts/create_post.html')
        cache.clear()


class PostsContextTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Test')
        cls.user2 = User.objects.create_user(username='Test2')
        cls.follower = User.objects.create_user(username='Follower')
        cls.not_follower = User.objects.create_user(username='Not_follower')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание группы',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized2_client = Client()
        self.authorized2_client.force_login(self.user2)
        self.follower_client = Client()
        self.follower_client.force_login(self.follower)
        self.not_follower_client = Client()
        self.not_follower_client.force_login(self.not_follower)

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

    def check_attributes(self, test_data):
        self.assertEqual(self.post.text, test_data.text)

    def check_attribute_image(self, test_data):
        self.assertEqual(self.post.image, test_data.image)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
        )
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.check_attributes(first_object)
        self.check_attribute_image(first_object)
        cache.clear()

    def test_group_list_pages_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
        )
        response = (self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test_group'})))
        self.assertEqual(
            response.context.get('group').title,
            'Тестовая группа'
        )
        self.assertEqual(response.context.get('group').slug, 'test_group')
        self.assertEqual(
            response.context.get('group').description,
            'Тестовое описание группы'
        )
        cache.clear()

    def test_profile_pages_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
        )
        response = (self.authorized_client.get(
            reverse('posts:profile', kwargs={
                'username': f'{PostsContextTests.user.username}'})))
        first_object = response.context['page_obj'][0]
        self.check_attributes(first_object)
        self.check_attribute_image(first_object)
        cache.clear()

    def test_post_with_group_on_the_correct_pages(self):
        '''Пост, созданный с указанием группы,
        отображается на соответствующих страницах:
        /index;
        /group/test_group/;
        /posts/profile/<username>.
        '''
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
        )
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.check_attributes(first_object)
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={
                'username': f'{PostsContextTests.user.username}'}))
        first_object = response.context['page_obj'][0]
        self.check_attributes(first_object)
        self.check_attribute_image(first_object)
        cache.clear()

    def test_cache_index(self):
        """ Проверка работы кэширования для
        страницы index """
        template_for_check = 'posts:index'
        response_0 = self.authorized_client.get(reverse(template_for_check))
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
        )
        response_1 = self.authorized_client.get(reverse(template_for_check))
        self.assertEqual(response_0.content, response_1.content)
        cache.clear()
        response_2 = self.authorized_client.get(reverse(template_for_check))
        self.assertNotEqual(response_1.content, response_2.content)
        cache.clear()

    def test_follow_unfollow(self):
        """ Проверка функции подписки и отписки"""
        created = Follow.objects.get_or_create(
            user=self.follower,
            author=self.user
        )
        checked_follow = Follow.objects.filter(
            user=self.follower,
            author=self.user
        )
        self.assertTrue(checked_follow.exists())

        created.delete()
        Follow.objects.filter(
            user=self.follower,
            author=self.user
        )
        self.assertFalse(checked_follow.exists())
        cache.clear()

    def test_follow_unfollow(self):
        """
        Проверка отображения новой записи пользователя
        в ленте тех, кто на него подписан;
        Проверка того, что отображение новой записи пользователя
        в ленте тех, кто на него не подписан не происходит
        """
        Follow.objects.get_or_create(
            user=self.follower,
            author=self.user
        )
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост для подписчиков',
        )

        response_follower = (self.follower_client.get(
            reverse('posts:follow_index')))
        followers_object = response_follower.context['page_obj'][0]
        self.assertEqual(followers_object.author, self.post.author)

        response_not_follower = (self.not_follower_client.get(
            reverse('posts:follow_index')))
        self.assertNotEqual(response_not_follower, response_follower)
