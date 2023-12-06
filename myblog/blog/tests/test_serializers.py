from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import dateparse

from blog.models import Post, Comment
from blog.serializers import AuthorInfoSerializer, PostSerializer, PostDetailSerializer, CommentSerializer


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


class PostDetailSerializerTestCase(TestCase):
    def setUp(self):
        self.test_user_1 = User.objects.create(username='user_1')
        self.test_user_2 = User.objects.create(username='user_2')

        self.post_1 = Post.objects.create(title='Some post', body='Some body',
                                          author=self.test_user_1, status='PB')

        self.comment_1 = Comment.objects.create(author=self.test_user_2, post=self.post_1,
                               body='Comment 1')
        self.comment_2 = Comment.objects.create(author=self.test_user_2, post=self.post_1,
                               body='Comment 2')

    def test_post_detail_serializer_with_fields(self):
        post = Post.objects.get(id=self.post_1.id)
        serialized_data = PostDetailSerializer(post, fields=(
            'id', 'title',
            'body', 'comments',
        )).data
        expected_data = {
            'id': self.post_1.id,
            'title': 'Some post',
            'body': 'Some body',
            'comments': [
                {
                    'id': self.comment_1.id,
                    'author': {
                        'id': self.test_user_2.id,
                        'first_name': self.test_user_2.first_name,
                        'last_name': self.test_user_2.last_name
                    },
                    'body': self.comment_1.body,
                    'created': self.comment_1.created,
                    'updated': self.comment_1.updated
                },
                {
                    'id': self.comment_2.id,
                    'author': {
                        'id': self.test_user_2.id,
                        'first_name': self.test_user_2.first_name,
                        'last_name': self.test_user_2.last_name
                    },
                    'body': self.comment_2.body,
                    'created': self.comment_2.created,
                    'updated': self.comment_2.updated
                },
            ]
        }
        for comment in serialized_data['comments']:
            comment['created'] = dateparse.parse_datetime(comment['created'])
            comment['updated'] = dateparse.parse_datetime(comment['updated'])
        self.assertEqual(expected_data, serialized_data)

    def test_post_detail_serializer_without_fields(self):
        post = Post.objects.get(id=self.post_1.id)
        serialized_data = PostDetailSerializer(post).data
        expected_data = {
            'id': self.post_1.id,
            'author': {
                'id': self.test_user_1.id,
                'first_name': self.test_user_1.first_name,
                'last_name': self.test_user_1.last_name
            },
            'title': 'Some post',
            'body': 'Some body',
            'status': 'PB',
            'created': self.post_1.created,
            'updated': self.post_1.updated,
            'comments': [
                {
                    'id': self.comment_1.id,
                    'author': {
                        'id': self.test_user_2.id,
                        'first_name': self.test_user_2.first_name,
                        'last_name': self.test_user_2.last_name
                    },
                    'body': self.comment_1.body,
                    'created': self.comment_1.created,
                    'updated': self.comment_1.updated
                },
                {
                    'id': self.comment_2.id,
                    'author': {
                        'id': self.test_user_2.id,
                        'first_name': self.test_user_2.first_name,
                        'last_name': self.test_user_2.last_name
                    },
                    'body': self.comment_2.body,
                    'created': self.comment_2.created,
                    'updated': self.comment_2.updated
                },
            ]
        }

        serialized_data['created'] = dateparse.parse_datetime(serialized_data['created'])
        serialized_data['updated'] = dateparse.parse_datetime(serialized_data['updated'])
        for comment in serialized_data['comments']:
            comment['created'] = dateparse.parse_datetime(comment['created'])
            comment['updated'] = dateparse.parse_datetime(comment['updated'])
        self.assertEqual(expected_data, serialized_data)


class CommentSerializerTestCase(TestCase):
    def setUp(self):
        self.test_user_1 = User.objects.create(username='user_1')
        self.test_user_2 = User.objects.create(username='user_2')

        self.post = Post.objects.create(title='Some post', body='Some body', author=self.test_user_1,
                                        status='PB')
        self.comment = Comment.objects.create(body='Some comment', author=self.test_user_2, post=self.post)

    def test_comment_serializer(self):
        serialized_data = CommentSerializer(self.comment).data
        expected_data = {
            'id': self.comment.id,
            'author': {
                'id': self.test_user_2.id,
                'first_name': self.test_user_2.first_name,
                'last_name': self.test_user_2.last_name
            },
            'body': 'Some comment',
            'created': self.comment.created,
            'updated': self.comment.updated
        }
        serialized_data['created'] = dateparse.parse_datetime(serialized_data['created'])
        serialized_data['updated'] = dateparse.parse_datetime(serialized_data['updated'])
        self.assertEqual(expected_data, serialized_data)
