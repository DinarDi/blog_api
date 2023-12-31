import json

from django.contrib.auth.models import User
from django.db.models import Count, Case, When
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase, APIClient

from blog.models import Post, Comment, UserPostRelation
from blog.serializers import PostSerializer, PostDetailSerializer, CommentSerializer, UserPostRelationSerializer


class GeneralMethodsForTest:
    """
    Methods for test
    """
    @staticmethod
    def get_client(user: User):
        """
        Function to create authenticated client
        :param user: User
        :return: APIClient
        """
        api_user = APIClient()
        api_user.force_authenticate(user=user)
        return api_user


class PostApiTestCase(APITestCase, GeneralMethodsForTest):
    def setUp(self):
        self.test_user_1 = User.objects.create(username='test_user_1')
        self.test_user_2 = User.objects.create(username='test_user_2')
        self.test_user_3 = User.objects.create(username='test_user_3',
                                               is_staff=True)

        self.post_1 = Post.objects.create(title='Some post new', body='Some body',
                                          author=self.test_user_1, status='PB')
        self.post_2 = Post.objects.create(title='Some post 2', body='Some body 2',
                                          author=self.test_user_2, status='PB')
        self.post_3 = Post.objects.create(title='Some post 3', body='Some body new 3',
                                          author=self.test_user_1, status='PB')
        self.post_4 = Post.objects.create(title='Some post 4', body='Some body new 4',
                                          author=self.test_user_1, status='DF')

        self.relation = UserPostRelation.objects.create(user=self.test_user_1, post=self.post_2, like=True)

    def test_get_posts(self):
        url = reverse('post-list')
        posts = Post.objects.filter(status='PB').annotate(
            likes_count=Count(Case(When(userpostrelation__like=True, then=1))),
            bookmarks_count=Count(Case(When(userpostrelation__in_bookmarks=True, then=1)))
        )
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(posts.count(), response.data['count'])

        serialized_data = PostSerializer(posts, many=True,
                                         fields=(
                                             'id', 'author', 'title',
                                             'body', 'likes_count', 'bookmarks_count',
                                             'created', 'updated'
                                         )).data
        self.assertEqual(serialized_data[:2], response.data['results'])

    def test_get_my_posts(self):
        url = reverse('post-my-posts')
        user = self.get_client(self.test_user_1)
        posts = Post.objects.filter(author=self.test_user_1).annotate(
            likes_count=Count(Case(When(userpostrelation__like=True, then=1))),
            bookmarks_count=Count(Case(When(userpostrelation__in_bookmarks=True, then=1)))
        )
        response = user.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(posts.count(), response.data['count'])

        serialized_data = PostSerializer(posts, many=True,
                                         fields=(
                                             'id', 'title', 'body', 'likes_count',
                                             'bookmarks_count', 'status'
                                         )).data
        self.assertEqual(serialized_data[:2], response.data['results'])

    def test_get_one_post(self):
        url = reverse('post-detail', args=(self.post_2.id, ))
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        post = Post.objects.all().annotate(
            likes_count=Count(Case(When(userpostrelation__like=True, then=1))),
            bookmarks_count=Count(Case(When(userpostrelation__in_bookmarks=True, then=1)))
        ).get(id=self.post_2.id)
        serialized_data = PostDetailSerializer(post, fields=('id', 'author', 'title',
                                                             'body', 'likes_count',
                                                             'bookmarks_count', 'comments')).data
        self.assertEqual(serialized_data, response.data)

    def test_search_posts(self):
        url = reverse('post-list')
        posts = Post.objects.filter(id__in=[self.post_1.id, self.post_3.id]).annotate(
            likes_count=Count(Case(When(userpostrelation__like=True, then=1))),
            bookmarks_count=Count(Case(When(userpostrelation__in_bookmarks=True, then=1)))
        ).order_by('id')

        response = self.client.get(url, data={'search': 'new'})
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(posts.count(), response.data['count'])

        serialized_data = PostSerializer(posts, many=True,
                                         fields=(
                                             'id', 'author', 'title',
                                             'body', 'likes_count', 'bookmarks_count',
                                             'created', 'updated'
                                         )).data
        self.assertEqual(serialized_data, response.data['results'])

    def test_order_posts_plus(self):
        url = reverse('post-list')
        posts = Post.objects.filter(status='PB').annotate(
            likes_count=Count(Case(When(userpostrelation__like=True, then=1))),
            bookmarks_count=Count(Case(When(userpostrelation__in_bookmarks=True, then=1)))
        ).order_by('created')

        response = self.client.get(url, data={'ordering': 'created'})
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(posts.count(), response.data['count'])

        serialized_data = PostSerializer(posts, many=True,
                                         fields=(
                                             'id', 'author', 'title',
                                             'body', 'likes_count', 'bookmarks_count',
                                             'created', 'updated'
                                         )).data
        self.assertEqual(serialized_data[:2], response.data['results'])

    def test_order_posts_minus(self):
        url = reverse('post-list')
        posts = Post.objects.filter(status='PB').annotate(
            likes_count=Count(Case(When(userpostrelation__like=True, then=1))),
            bookmarks_count=Count(Case(When(userpostrelation__in_bookmarks=True, then=1)))
        ).order_by('-created')

        response = self.client.get(url, data={'ordering': '-created'})
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(posts.count(), response.data['count'])

        serialized_data = PostSerializer(posts, many=True,
                                         fields=(
                                             'id', 'author', 'title',
                                             'body', 'likes_count', 'bookmarks_count',
                                             'created', 'updated'
                                         )).data
        self.assertEqual(serialized_data[:2], response.data['results'])

    def test_create_post(self):
        count_before = Post.objects.all().count()
        self.assertEqual(4, count_before)

        url = reverse('post-list')
        data = {
            'title': 'New post',
            'body': 'New body'
        }
        json_data = json.dumps(data)

        api_client = self.get_client(self.test_user_1)
        response = api_client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        last_elem = Post.objects.last()
        self.assertEqual(data['title'], last_elem.title)
        self.assertEqual(data['body'], last_elem.body)

        count_after = Post.objects.all().count()
        self.assertEqual(5, count_after)

    def test_update_post(self):
        # Can update if change status to DF
        url = reverse('post-detail', args=(self.post_1.id, ))
        api_client = self.get_client(self.test_user_1)

        data = {
            'title': 'New title',
            'status': 'DF'
        }
        json_data = json.dumps(data)
        response = api_client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.post_1.refresh_from_db()
        self.assertEqual('New title', self.post_1.title)

    def test_update_post_wrong(self):
        # Should return 403 because status has not been changed to DF
        url = reverse('post-detail', args=(self.post_1.id, ))
        api_client = self.get_client(self.test_user_1)

        data = {
            'title': 'New title',
        }
        json_data = json.dumps(data)
        response = api_client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.post_1.refresh_from_db()
        self.assertEqual('Some post new', self.post_1.title)

    def test_update_post_not_owner(self):
        # Should return 403
        url = reverse('post-detail', args=(self.post_1.id, ))
        api_client = self.get_client(self.test_user_2)

        data = {
            'title': 'New title',
            'status': 'DF'
        }
        json_data = json.dumps(data)
        response = api_client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.post_1.refresh_from_db()
        self.assertEqual('Some post new', self.post_1.title)

    def test_update_post_staff(self):
        # Can update if change status to DF
        url = reverse('post-detail', args=(self.post_1.id, ))
        api_client = self.get_client(self.test_user_3)

        data = {
            'title': 'New title',
            'status': 'DF'
        }
        json_data = json.dumps(data)
        response = api_client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.post_1.refresh_from_db()
        self.assertEqual('New title', self.post_1.title)

    def test_delete_post(self):
        url = reverse('post-detail', args=(self.post_1.id, ))
        post_count_before = Post.objects.all().count()
        self.assertEqual(4, post_count_before)

        api_client = self.get_client(self.test_user_1)
        response = api_client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

        post_count_after = Post.objects.all().count()
        self.assertEqual(3, post_count_after)

    def test_delete_post_not_owner(self):
        # Should return 403
        url = reverse('post-detail', args=(self.post_1.id, ))
        post_count_before = Post.objects.all().count()
        self.assertEqual(4, post_count_before)

        api_client = self.get_client(self.test_user_2)
        response = api_client.delete(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

        post_count_after = Post.objects.all().count()
        self.assertEqual(4, post_count_after)

    def test_delete_post_staff(self):
        url = reverse('post-detail', args=(self.post_1.id, ))
        post_count_before = Post.objects.all().count()
        self.assertEqual(4, post_count_before)

        api_client = self.get_client(self.test_user_3)
        response = api_client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

        post_count_after = Post.objects.all().count()
        self.assertEqual(3, post_count_after)


class PaginationTestCase(APITestCase, GeneralMethodsForTest):
    def setUp(self):
        self.test_user_1 = User.objects.create(username='test_user_1')
        self.test_user_2 = User.objects.create(username='test_user_2')

        self.post_1 = Post.objects.create(title='Some post new', body='Some body',
                                          author=self.test_user_1, status="PB")
        self.post_2 = Post.objects.create(title='Some post 2', body='Some body 2',
                                          author=self.test_user_2, status="PB")
        self.post_3 = Post.objects.create(title='Some post 3', body='Some body new 3',
                                          author=self.test_user_1, status="PB")
        self.post_4 = Post.objects.create(title='Some post new', body='Some body post',
                                          author=self.test_user_1, status="PB")

        self.comment_1 = Comment.objects.create(author=self.test_user_1, post=self.post_2,
                                                body='Test comment 1')
        self.comment_2 = Comment.objects.create(author=self.test_user_1, post=self.post_2,
                                                body='Test comment 2')
        self.comment_2 = Comment.objects.create(author=self.test_user_1, post=self.post_2,
                                                body='Test comment 3')

    def test_pagination_posts(self):
        url = reverse('post-list')
        api_client = self.get_client(self.test_user_1)

        response_1 = api_client.get(url)
        self.assertEqual(status.HTTP_200_OK, response_1.status_code)

        posts = Post.objects.filter(status='PB').annotate(
            likes_count=Count(Case(When(userpostrelation__like=True, then=1))),
            bookmarks_count=Count(Case(When(userpostrelation__in_bookmarks=True, then=1)))
        )
        serialized_data = PostSerializer(posts, many=True,
                                         fields=(
                                             'id', 'author', 'title',
                                             'body', 'likes_count',
                                             'bookmarks_count', 'created', 'updated'
                                         )).data
        expected_data_page_1 = {
            'count': posts.count(),
            'next': 'http://testserver/api/posts/?page_size=2',
            'previous': None,
            'results': serialized_data[:2]
        }
        self.assertEqual(expected_data_page_1, response_1.data)

        response_2 = api_client.get(response_1.data['next'])
        self.assertEqual(status.HTTP_200_OK, response_2.status_code)

        expected_data_page_2 = {
            'count': posts.count(),
            'next': None,
            'previous': 'http://testserver/api/posts/',
            'results': serialized_data[2:]
        }
        self.assertEqual(expected_data_page_2, response_2.data)

    def test_pagination_posts_wrong(self):
        url = reverse('post-list')
        api_client = self.get_client(self.test_user_1)
        response = api_client.get(url, {'page_size': 10000})
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

        expected_data = {
            'detail': ErrorDetail(string='Invalid page.', code='not_found')
        }
        self.assertEqual(expected_data, response.data)

        response_2 = api_client.get(url, {'page_size': 'asdas'})
        self.assertEqual(expected_data, response_2.data)

    def test_my_posts_pagination(self):
        url = reverse('post-my-posts')
        api_client = self.get_client(self.test_user_1)
        posts = Post.objects.filter(author=self.test_user_1).annotate(
            likes_count=Count(Case(When(userpostrelation__like=True, then=1))),
            bookmarks_count=Count(Case(When(userpostrelation__in_bookmarks=True, then=1)))
        )

        response_1 = api_client.get(url)
        self.assertEqual(status.HTTP_200_OK, response_1.status_code)

        serialized_data = PostSerializer(posts, many=True,
                                         fields=(
                                             'id', 'title', 'body',
                                             'likes_count', 'bookmarks_count', 'status'
                                         )).data
        expected_data_1 = {
            'count': posts.count(),
            'next': 'http://testserver/api/posts/my_posts/?page_size=2',
            'previous': None,
            'results': serialized_data[:2]
        }
        self.assertEqual(expected_data_1, response_1.data)

        response_2 = api_client.get(response_1.data['next'])
        self.assertEqual(status.HTTP_200_OK, response_2.status_code)

        expected_data_2 = {
            'count': posts.count(),
            'next': None,
            'previous': 'http://testserver/api/posts/my_posts/',
            'results': serialized_data[2:]
        }
        self.assertEqual(expected_data_2, response_2.data)

    def test_my_posts_pagination_wrong(self):
        url = reverse('post-my-posts')
        api_client = self.get_client(self.test_user_1)

        response_1 = api_client.get(url, {'page_size': 10000})
        self.assertEqual(status.HTTP_404_NOT_FOUND, response_1.status_code)

        expected_data = {
            'detail': ErrorDetail(string='Invalid page.', code='not_found')
        }
        self.assertEqual(expected_data, response_1.data)

        response_2 = api_client.get(url, {'page_size': 'asd'})
        self.assertEqual(status.HTTP_404_NOT_FOUND, response_2.status_code)
        self.assertEqual(expected_data, response_2.data)

    def test_my_comments_pagination(self):
        url = reverse('comment-my-comments')
        api_client = self.get_client(self.test_user_1)
        comments = Comment.objects.filter(author=self.test_user_1)
        response_1 = api_client.get(url)
        self.assertEqual(status.HTTP_200_OK, response_1.status_code)

        serialized_data = CommentSerializer(comments, many=True, fields=('id', 'body',
                                                                         'created', 'updated')).data
        expected_data_1 = {
            'count': comments.count(),
            'next': 'http://testserver/api/comments/my_comments/?page_size=2',
            'previous': None,
            'results': serialized_data[:2]
        }
        self.assertEqual(expected_data_1, response_1.data)

        response_2 = api_client.get(response_1.data['next'])
        self.assertEqual(status.HTTP_200_OK, response_2.status_code)

        expected_data_2 = {
            'count': comments.count(),
            'next': None,
            'previous': 'http://testserver/api/comments/my_comments/',
            'results': serialized_data[2:]
        }
        self.assertEqual(expected_data_2, response_2.data)


class CommentsApiTestCase(APITestCase, GeneralMethodsForTest):
    def setUp(self):
        self.test_user_1 = User.objects.create(username='test_user_1', first_name='Name',
                                               last_name='Another')
        self.test_user_2 = User.objects.create(username='test_user_2', first_name='MyName')
        self.test_user_3 = User.objects.create(username='test_user_3',
                                               is_staff=True)

        self.post_1 = Post.objects.create(title='Some post new', body='Some body',
                                          author=self.test_user_1, status='PB')
        self.post_2 = Post.objects.create(title='Some post 2', body='Some body 2',
                                          author=self.test_user_2, status='PB')
        self.post_3 = Post.objects.create(title='Some post 3', body='Some body new 3',
                                          author=self.test_user_1, status='PB')

        self.comment = Comment.objects.create(author=self.test_user_1, post=self.post_1, body='Test comment')

    def test_add_comment(self):
        url = reverse('post-add-comment', args=(self.post_2.id, ))
        api_client = self.get_client(self.test_user_1)
        data = {
            'body': 'Test comment'
        }
        json_data = json.dumps(data)
        response = api_client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        comments_count = self.post_2.comments.count()
        self.assertEqual(1, comments_count)
        self.assertEqual('Test comment', self.post_2.comments.last().body)

    def test_get_my_comments(self):
        url = reverse('comment-my-comments')
        api_client = self.get_client(self.test_user_1)
        response = api_client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        comments = Comment.objects.filter(author=self.test_user_1)
        serialized_data = CommentSerializer(comments, many=True,
                                            fields=('id', 'body', 'created', 'updated')).data
        self.assertEqual(serialized_data, response.data['results'])

    def test_owner_get_comment(self):
        url = reverse('comment-detail', args=(self.comment.id, ))
        api_client = self.get_client(self.test_user_1)
        response = api_client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        post = Comment.objects.get(id=self.comment.id)
        serialized_data = CommentSerializer(post, fields=('id', 'body',
                                                          'created', 'updated')).data
        self.assertEqual(serialized_data, response.data)

    def test_not_owner_get_comment(self):
        url = reverse('comment-detail', args=(self.comment.id, ))
        api_client = self.get_client(self.test_user_2)
        response = api_client.get(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_staff_get_comment(self):
        url = reverse('comment-detail', args=(self.comment.id, ))
        api_client = self.get_client(self.test_user_3)
        response = api_client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        post = Comment.objects.get(id=self.comment.id)
        serialized_data = CommentSerializer(post, fields=('id', 'author', 'body',
                                                          'created', 'updated')).data
        self.assertEqual(serialized_data, response.data)

    def test_update_comment(self):
        url = reverse('comment-detail', args=(self.comment.id, ))
        api_client = self.get_client(self.test_user_1)
        data = {
            'body': 'Update comment'
        }
        json_data = json.dumps(data)
        response = api_client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.comment.refresh_from_db()
        self.assertEqual('Update comment', self.comment.body)

    def test_not_owner_update_comment(self):
        url = reverse('comment-detail', args=(self.comment.id,))
        api_client = self.get_client(self.test_user_2)
        data = {
            'body': 'Update comment'
        }
        json_data = json.dumps(data)
        response = api_client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.comment.refresh_from_db()
        self.assertEqual('Test comment', self.comment.body)

    def test_staff_update_comment(self):
        url = reverse('comment-detail', args=(self.comment.id,))
        api_client = self.get_client(self.test_user_3)
        data = {
            'body': 'Update comment'
        }
        json_data = json.dumps(data)
        response = api_client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.comment.refresh_from_db()
        self.assertEqual('Update comment', self.comment.body)

    def test_delete_comment(self):
        self.assertEqual(1, Comment.objects.filter(author=self.test_user_1).count())
        url = reverse('comment-detail', args=(self.comment.id, ))
        api_client = self.get_client(self.test_user_1)
        response = api_client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(0, Comment.objects.filter(author=self.test_user_1).count())

    def test_not_owner_delete_comment(self):
        self.assertEqual(1, Comment.objects.filter(author=self.test_user_1).count())
        url = reverse('comment-detail', args=(self.comment.id,))
        api_client = self.get_client(self.test_user_2)
        response = api_client.delete(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual(1, Comment.objects.filter(author=self.test_user_1).count())

    def test_staff_delete_comment(self):
        self.assertEqual(1, Comment.objects.filter(author=self.test_user_1).count())
        url = reverse('comment-detail', args=(self.comment.id, ))
        api_client = self.get_client(self.test_user_3)
        response = api_client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(0, Comment.objects.filter(author=self.test_user_1).count())


class UserPostRelationTestCase(APITestCase, GeneralMethodsForTest):
    def setUp(self):
        self.test_user_1 = User.objects.create(username='user_1')
        self.test_user_2 = User.objects.create(username='user_2')

        self.post = Post.objects.create(title='Some post', body='Some body', author=self.test_user_1,
                                        status='PB')

    def test_like(self):
        url = reverse('userpostrelation-detail', args=(self.post.id, ))
        api_client = self.get_client(self.test_user_2)

        # Like
        data_like = {
            'like': True
        }
        json_data = json.dumps(data_like)
        response = api_client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        relation = UserPostRelation.objects.get(user=self.test_user_2, post=self.post)
        serialized_data = UserPostRelationSerializer(relation).data
        self.assertEqual(response.data, serialized_data)

        # Unlike
        data_unlike = {
            'like': False
        }
        json_data = json.dumps(data_unlike)
        response = api_client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        relation.refresh_from_db()
        serialized_data = UserPostRelationSerializer(relation).data
        self.assertEqual(serialized_data, response.data)

    def test_bookmarks(self):
        url = reverse('userpostrelation-detail', args=(self.post.id, ))
        api_client = self.get_client(self.test_user_2)

        # Add bookmarks
        data_in = {
            'in_bookmarks': True
        }
        json_data = json.dumps(data_in)
        response = api_client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        relation = UserPostRelation.objects.get(user=self.test_user_2, post=self.post)
        serialized_data = UserPostRelationSerializer(relation).data
        self.assertEqual(response.data, serialized_data)

        # Unlike
        data_out = {
            'in_bookmarks': False
        }
        json_data = json.dumps(data_out)
        response = api_client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        relation.refresh_from_db()
        serialized_data = UserPostRelationSerializer(relation).data
        self.assertEqual(serialized_data, response.data)
