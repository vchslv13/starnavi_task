from urllib.parse import urlparse

from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.urls import reverse
from django.utils import dateparse

from social_network.models import Post, User


class UserViewSetTests(TestCase):
    def setUp(self):
        usr1 = User.objects.create_user(
            username='test1', email='test1@email.com', password='test1_pass')
        usr1.raw_password = 'test1_pass'
        usr2 = User.objects.create_user(
            username='test2', email='test2@email.com', password='test2_pass')
        usr2.raw_password = 'test2_pass'
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

    def test_unauthenticated_users_can_signup(self):
        test_data = {'email': 'test_email@email.com', 'username': 'test_name',
                     'full_name': 'test_fullname', 'password': 'test_password'}
        res = self.client.post(reverse('user-list'), data=test_data,
                               content_type='application/json')
        self.assertEqual(res.status_code, 201)
        self.assertIsNotNone(User.objects.get(email=test_data['email']))

    def test_user_cant_change_another_users_info(self):
        user1, user2 = self.users
        initial_user2_username = user2.username
        user1_auth = get_authorization_header(self.client, user1)

        # check initial state
        usr2_detail_url = reverse('user-detail', args=[user2.id])
        r = self.client.get(usr2_detail_url, **user1_auth)
        self.assertEqual(r.json()['username'], initial_user2_username)

        # try changing the information
        r = self.client.patch(
            usr2_detail_url, data={'username': 'very_bad_name'},
            content_type='application/json', **user1_auth)
        self.assertEqual(r.status_code, 401)

        del user2.username  # refresh field value from DB
        self.assertEqual(user2.username, initial_user2_username)


class PostViewSetTests(TestCase):
    def setUp(self):
        usr1 = User.objects.create_user(
            username='test1', email='test1@email.com', password='test1_pass')
        usr1.raw_password = 'test1_pass'
        usr2 = User.objects.create_user(
            username='test2', email='test2@email.com', password='test2_pass')
        usr2.raw_password = 'test2_pass'

        post1 = Post.objects.create(text='Test text 1', author=usr1)
        post2 = Post.objects.create(text='Test text 2', author=usr1)
        post3 = Post.objects.create(text='Test text 3', author=usr2)
        self.posts = [post1, post2, post3]
        self.users = [usr1, usr2]

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

    def test_authenticated_user_creates_post_associated_with_him(self):
        user = self.users[0]
        auth_header = get_authorization_header(self.client, user)

        # create post and check the result
        post = {'text': 'this is a test'}
        response = self.client.post(reverse('post-list'), data=post,
                                    content_type='application/json',
                                    **auth_header)
        self.assertEqual(response.status_code, 201)
        post_id = int(response.json()['id'])
        post = Post.objects.get(pk=post_id)
        self.assertEqual(post.author.id, user.id)

    def test_authenticated_user_likes_post(self):
        user = self.users[0]
        auth_header = get_authorization_header(self.client, user)

        post = self.posts[2]
        self.assertNotIn(user, post.liked_by_users.all())
        like_url = reverse('post-like', kwargs={'pk': post.id})
        self.client.post(like_url, **auth_header)
        self.assertIn(user, post.liked_by_users.all())

    def test_authenticated_user_unlikes_post(self):
        user = self.users[0]
        auth_header = get_authorization_header(self.client, user)

        post = self.posts[2]
        like_url = reverse('post-like', kwargs={'pk': post.id})
        self.client.post(like_url, **auth_header)
        self.assertIn(user, post.liked_by_users.all())

        unlike_url = reverse('post-unlike', kwargs={'pk': post.id})
        self.client.post(unlike_url, **auth_header)
        self.assertNotIn(user, post.liked_by_users.all())

    def test_user_cant_change_another_users_post(self):
        user1, user2 = self.users
        post = user2.post_set.all()[0]
        initial_post_text = post.text
        user1_auth = get_authorization_header(self.client, user1)

        # check initial state
        post_detail_url = reverse('post-detail', args=[post.id])
        r = self.client.get(post_detail_url, **user1_auth)
        self.assertEqual(r.json()['text'], initial_post_text)

        # try changing the information
        r = self.client.patch(
            post_detail_url, data={'text': 'very_bad_text'},
            content_type='application/json', **user1_auth)
        self.assertEqual(r.status_code, 401)

        del post.text
        self.assertEqual(post.text, initial_post_text)

    def test_user_can_create_post(self):
        user = self.users[0]
        intial_amount_of_posts = len(user.post_set.all())
        user_auth = get_authorization_header(self.client, user)
        r = self.client.post(reverse('post-list'), data={'text': 'test text'},
                             content_type='application/json', **user_auth)
        self.assertEqual(len(user.post_set.all()), intial_amount_of_posts + 1)

        try:
            Post.objects.get(pk=int(r.json()['id']))
        except ObjectDoesNotExist:
            raise AssertionError('post was not created')

    def test_user_can_update_post(self):
        user = self.users[0]
        post = user.post_set.all()[0]
        user_auth = get_authorization_header(self.client, user)
        new_text = 'new text'

        post_detail_url = reverse('post-detail', args=[post.id])
        r = self.client.patch(
            post_detail_url, data={'text': new_text},
            content_type='application/json', **user_auth)

        self.assertEqual(r.status_code, 200)
        del post.text
        self.assertEqual(post.text, new_text)


def get_authorization_header(client, user):
    """Get authorization header for user using the passed client."""
    # obtain authorization token
    response = client.post(
        reverse('token-obtain'),
        data={'username': user.username, 'password': user.raw_password},
        content_type='application/json'
    )
    token = response.json()['access']
    return {'HTTP_AUTHORIZATION': f'Bearer {token}'}
