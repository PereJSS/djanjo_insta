from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from posts.models import Post
from profiles.models import UserProfile


class PostLikeViewTests(TestCase):
	def setUp(self):
		self.author = User.objects.create_user(username='autor', password='secreto123')
		self.user = User.objects.create_user(username='lector', password='secreto123')
		UserProfile.objects.create(user=self.author)
		UserProfile.objects.create(user=self.user)
		self.post = Post.objects.create(user=self.author, imagen='post_images/test.jpg', content='Hola')

	def test_like_fallback_requires_post(self):
		self.client.force_login(self.user)

		response = self.client.get(reverse('like_post', kwargs={'pk': self.post.pk}))

		self.assertEqual(response.status_code, 405)
		self.assertFalse(self.post.likes.filter(pk=self.user.pk).exists())

	def test_like_fallback_post_redirects_to_safe_next_url(self):
		self.client.force_login(self.user)

		response = self.client.post(
			reverse('like_post', kwargs={'pk': self.post.pk}),
			{'next': f"{reverse('home')}#post-{self.post.pk}"},
		)

		self.assertRedirects(response, f"{reverse('home')}#post-{self.post.pk}", fetch_redirect_response=False)
		self.assertTrue(self.post.likes.filter(pk=self.user.pk).exists())
