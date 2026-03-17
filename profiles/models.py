from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    profile_picture = models.ImageField(verbose_name='Foto de perfil', upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(verbose_name='Biografía', max_length=500, blank=True)
    birth_date = models.DateField(verbose_name='Fecha de nacimiento', blank=True, null=True)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following', blank=True, through='Follow')

    class Meta:

        verbose_name = 'Perfil de usuario'
        verbose_name_plural = 'Perfiles de usuario'

    def __str__(self):
        return self.user.username
    
    def follow(self, profile):
        if profile != self:
            Follow.objects.get_or_create(follower=self, following=profile)

    def unfollow(self, profile):
        if profile != self:
            Follow.objects.filter(follower=self, following=profile).delete()
  
  
class Follow(models.Model):
    follower = models.ForeignKey(UserProfile, verbose_name='Seguidor', related_name='following_set', on_delete=models.CASCADE)
    following = models.ForeignKey(UserProfile, verbose_name='Siguiendo', related_name='followers_set', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de seguimiento')

    class Meta:
        unique_together = ('follower', 'following')
        verbose_name = 'Seguidor'
        verbose_name_plural = 'Seguidores'

    def __str__(self):
        return f"{self.follower.user.username} sigue a {self.following.user.username}"