from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from notifications.models import Notification


@method_decorator(login_required, name='dispatch')
class NotificationListView(ListView):
	model = Notification
	template_name = 'general/notification_list.html'
	context_object_name = 'notifications'

	def get(self, request, *args, **kwargs):
		Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
		return super().get(request, *args, **kwargs)

	def get_queryset(self):
		return Notification.objects.filter(recipient=self.request.user).select_related('actor')
