from django.conf import settings
from django.db import models


class Notification(models.Model):
	TYPE_FOLLOW = 'follow'
	TYPE_LIKE = 'like'
	TYPE_COMMENT = 'comment'

	TYPE_CHOICES = [
		(TYPE_FOLLOW, 'Nuevo seguidor'),
		(TYPE_LIKE, 'Me gusta'),
		(TYPE_COMMENT, 'Comentario'),
	]

	recipient = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		verbose_name='Destinatario',
		on_delete=models.CASCADE,
		related_name='notifications',
	)
	actor = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		verbose_name='Usuario que genera la notificación',
		on_delete=models.CASCADE,
		related_name='sent_notifications',
	)
	notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='Tipo')
	message = models.CharField(max_length=255, verbose_name='Mensaje')
	target_url = models.CharField(max_length=255, blank=True, verbose_name='URL de destino')
	is_read = models.BooleanField(default=False, verbose_name='Leída')
	created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')

	class Meta:
		ordering = ['-created_at']
		verbose_name = 'Notificación'
		verbose_name_plural = 'Notificaciones'

	def __str__(self):
		return f'Notificación para {self.recipient.username}: {self.message}'
