from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import dateparse

from blog.models import Post
from blog.serializers import AuthorInfoSerializer, PostSerializer


class AuthorInfoSerializerTestCase(TestCase):
    def setUp(self):
        self.test_user_1 = User.objects.create(username='user_1', first_name='Name',
                                               last_name='LastName')

    def test_author_info_serializer(self):
        serialized_data = AuthorInfoSerializer(self.test_user_1).data
        expected_data = {
            'id': self.test_user_1.id,
            'first_name': 'Name',
            'last_name': 'LastName'
        }
        self.assertEqual(expected_data, serialized_data)


class PostSerializerTestCase(TestCase):
    def setUp(self):
        self.test_user_1 = User.objects.create(username='user_1', first_name='Name_1',
                                               last_name='LastName_1')
        self.test_user_2 = User.objects.create(username='user_2', first_name='Name_2',
                                               last_name='LastName_2')

        self.post_1 = Post.objects.create(title='Some post 1', body='Some body 1',
                                          author=self.test_user_1, status='PB')
        self.post_2 = Post.objects.create(title='Some post 2', body='Some body 2',
                                          author=self.test_user_2, status='PB')
        self.post_3 = Post.objects.create(title='Some post 3', body='Some body 3',
                                          author=self.test_user_2, status='PB')

    def test_post_serializer_with_fields(self):
        posts = Post.objects.all()
        serialized_data = PostSerializer(posts, many=True,
                                         fields=('id', 'title', 'body')).data
        expected_data = [
            {
                'id': self.post_1.id,
                'title': 'Some post 1',
                'body': 'Some body 1'
            },
            {
                'id': self.post_2.id,
                'title': 'Some post 2',
                'body': 'Some body 2'
            },
            {
                'id': self.post_3.id,
                'title': 'Some post 3',
                'body': 'Some body 3'
            },
        ]
        self.assertEqual(expected_data, serialized_data)

    def test_post_serializer_without_fields(self):
        posts = Post.objects.all().order_by('id')
        serialized_data = PostSerializer(posts, many=True).data
        expected_data = [
            {
                'id': self.post_1.id,
                'author': {
                    'id': self.test_user_1.id,
                    'first_name': self.test_user_1.first_name,
                    'last_name': self.test_user_1.last_name
                },
                'title': 'Some post 1',
                'body': 'Some body 1',
                'status': 'PB',
                'created': self.post_1.created,
                'updated': self.post_1.updated
            },
            {
                'id': self.post_2.id,
                'author': {
                    'id': self.test_user_2.id,
                    'first_name': self.test_user_2.first_name,
                    'last_name': self.test_user_2.last_name
                },
                'title': 'Some post 2',
                'body': 'Some body 2',
                'status': 'PB',
                'created': self.post_2.created,
                'updated': self.post_2.updated
            },
            {
                'id': self.post_3.id,
                'author': {
                    'id': self.test_user_2.id,
                    'first_name': self.test_user_2.first_name,
                    'last_name': self.test_user_2.last_name
                },
                'title': 'Some post 3',
                'body': 'Some body 3',
                'status': 'PB',
                'created': self.post_3.created,
                'updated': self.post_3.updated
            },
        ]
        for data in serialized_data:
            data['created'] = dateparse.parse_datetime(data['created'])
            data['updated'] = dateparse.parse_datetime(data['updated'])
        self.assertEqual(expected_data, serialized_data)
