from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from profiles.models import UserProfile


class ProfileRenderingTests(TestCase):
	def test_home_renders_for_authenticated_user_without_existing_profile(self):
		user_without_profile = User.objects.create_user(username='sinperfil', password='secreto123')
		self.client.force_login(user_without_profile)

		response = self.client.get(reverse('home'))

		self.assertEqual(response.status_code, 200)
		self.assertTrue(UserProfile.objects.filter(user=user_without_profile).exists())

	def test_other_profile_uses_third_person_copy(self):
		viewer = User.objects.create_user(username='viewer', password='secreto123')
		owner = User.objects.create_user(username='owner', password='secreto123')
		UserProfile.objects.create(user=viewer)
		owner_profile = UserProfile.objects.create(user=owner)
		self.client.force_login(viewer)

		response = self.client.get(reverse('profile_detail', kwargs={'pk': owner_profile.pk}))

		self.assertContains(response, 'Publicaciones de owner')
		self.assertContains(response, 'owner todavía no ha publicado nada.')
