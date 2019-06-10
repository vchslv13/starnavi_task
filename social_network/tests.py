from urllib.parse import urlparse

from django.urls import reverse, resolve
from django.test import TestCase
from django.utils import dateparse

from social_network.models import Post, User


class UserViewSetTests(TestCase):
    def setUp(self):
        usr1 = User.objects.create_user(
            username='test1', email='test1@email.com', password='test1_pass')
        usr2 = User.objects.create_user(
            username='test2', email='test2@email.com', password='test2_pass')
        self.users = [usr1, usr2]

    def test_unauthenticated_users_retrieve_user_list(self):
        response = self.client.get(reverse('user-list'))
        self.assertEqual(len(response.json()), len(self.users))

        usr_ids = {usr.id for usr in self.users}
        res_usr_ids = {usr['id'] for usr in response.json()}
        self.assertEqual(usr_ids, res_usr_ids)

    def test_unauthenticated_users_retrieve_user_detail(self):
        usr = self.users[0]
        path = reverse('user-detail', kwargs={'pk': usr.id})
        res_json = self.client.get(path).json()

        self.assertEqual(res_json['id'], usr.id)
        self.assertEqual(res_json['email'], usr.email)
        self.assertEqual(res_json['username'], usr.username)
        self.assertEqual(res_json['full_name'], usr.full_name)
        self.assertEqual(dateparse.parse_datetime(res_json['date_joined']),
                         usr.date_joined)
        self.assertNotIn('password', res_json)

    def test_unauthenticated_users_cant_update_user_detail(self):
        usr = self.users[0]
        path = reverse('user-detail', kwargs={'pk': usr.id})
        test_data = {'email': 'test_email@email.com', 'username': 'test_name',
                     'full_name': 'test_fullname'}

        res = self.client.patch(path, data={'email': test_data['email']},
                                content_type='application/json')
        self.assertEqual(res.status_code, 401)

        res = self.client.put(path, data=test_data,
                              content_type='application/json')
        self.assertEqual(res.status_code, 401)


class PostViewSetTests(TestCase):
    def setUp(self):
        usr1 = User.objects.create_user(
            username='test1', email='test1@email.com', password='test1_pass')
        usr2 = User.objects.create_user(
            username='test2', email='test2@email.com', password='test2_pass')
        post1 = Post.objects.create(text='Test text 1', author=usr1)
        post2 = Post.objects.create(text='Test text 2', author=usr1)
        post3 = Post.objects.create(text='Test text 3', author=usr2)
        self.posts = [post1, post2, post3]

    def test_unauthenticated_users_retrieve_posts_list(self):
        response = self.client.get(reverse('post-list'))
        self.assertEqual(len(response.json()), len(self.posts))

        post_ids = {post.id for post in self.posts}
        res_post_ids = {post['id'] for post in response.json()}
        self.assertEqual(post_ids, res_post_ids)

    def test_unauthenticated_users_retrieve_post_detail(self):
        post = self.posts[0]
        path = reverse('post-detail', kwargs={'pk': post.id})
        res_json = self.client.get(path).json()

        self.assertEqual(res_json['id'], post.id)
        self.assertEqual(res_json['text'], post.text)

        author_path = reverse('user-detail', kwargs={'pk': post.author.id})
        self.assertEqual(urlparse(res_json['author']).path,
                         author_path)

    def test_unauthenticated_users_cant_update_post_detail(self):
        post = self.posts[0]
        path = reverse('post-detail', kwargs={'pk': post.id})
        author_url = reverse('user-detail', kwargs={'pk': post.author.id})
        test_data = {'text': 'Test text X', 'author': author_url}

        res = self.client.patch(path, data={'text': test_data['text']},
                                content_type='application/json')
        self.assertEqual(res.status_code, 401)

        res = self.client.put(path, data=test_data,
                              content_type='application/json')
        self.assertEqual(res.status_code, 401)
