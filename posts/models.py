from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Post(models.Model):
    user = models.ForeignKey(User, verbose_name='Autor', on_delete=models.CASCADE, related_name='posts')
    imagen = models.ImageField(verbose_name='Imagen', upload_to='post_images/')
    content = models.TextField(verbose_name='Contenido')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    likes = models.ManyToManyField(User, verbose_name='Me gusta', related_name='liked_posts', blank=True,)

    class Meta:
        verbose_name = 'Publicación'
        verbose_name_plural = 'Publicaciones'

    def __str__(self):
        return f"{self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
    

class Comment(models.Model):
    post = models.ForeignKey(Post, verbose_name='Publicación', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, verbose_name='Autor del comentario', on_delete=models.CASCADE)
    content = models.TextField(verbose_name='Contenido del comentario')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')

    class Meta:
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'

    def __str__(self):
        return f"{self.user.username} comenta en {self.post.id} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"