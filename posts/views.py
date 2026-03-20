from django.views.generic.edit import CreateView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic.detail import DetailView

from notifications.models import Notification
from posts.forms import PostCommentCreateForm, PostCreateForm
from posts.models import Post
from posts.services import (
    build_like_toggle_message,
    get_posts_queryset_for_display,
    toggle_post_like_for_user,
)

@method_decorator(login_required, name='dispatch')
class PostCreateView(CreateView):
    model = Post
    template_name = 'posts/post_create.html'
    form_class = PostCreateForm
    success_url = reverse_lazy('home')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.add_message(self.request, messages.SUCCESS, 'Publicación creada correctamente.')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return get_posts_queryset_for_display(Post.objects.all(), self.request.user)


@login_required    
@require_POST
def toggle_post_like_view(request, pk):
    selected_post = get_object_or_404(Post, pk=pk)
    user_liked_post = toggle_post_like_for_user(post=selected_post, acting_user=request.user)
    messages.add_message(request, messages.SUCCESS, build_like_toggle_message(user_liked_post))

    redirect_target = request.POST.get('next', '')
    if redirect_target and url_has_allowed_host_and_scheme(
        url=redirect_target,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(redirect_target)

    return redirect('post_detail', pk=pk)


@login_required
@require_POST
def toggle_post_like_ajax_view(request, pk):
    selected_post = get_object_or_404(Post, pk=pk)
    user_liked_post = toggle_post_like_for_user(post=selected_post, acting_user=request.user)
    return JsonResponse(
        {
            'liked': user_liked_post,
            'likes_count': selected_post.likes.count(),
            'message': build_like_toggle_message(user_liked_post),
        }
    )


@login_required
@require_POST
def create_post_comment_view(request, pk):
    selected_post = get_object_or_404(Post, pk=pk)
    comment_create_form = PostCommentCreateForm(request.POST)
    redirect_target = request.POST.get('next', '')

    if comment_create_form.is_valid():
        comment_content = comment_create_form.cleaned_data['content']
        try:
            selected_post.add_comment(author_user=request.user, comment_content=comment_content)

            if selected_post.user_id != request.user.id:
                Notification.objects.create(
                    recipient=selected_post.user,
                    actor=request.user,
                    notification_type=Notification.TYPE_COMMENT,
                    message=f"{request.user.username} ha comentado tu publicación.",
                    target_url=reverse('post_detail', kwargs={'pk': selected_post.pk}),
                )

            messages.add_message(request, messages.SUCCESS, 'Comentario publicado correctamente.')
        except ValueError:
            messages.add_message(request, messages.ERROR, 'No se pudo publicar el comentario.')
    else:
        messages.add_message(request, messages.ERROR, 'El comentario no es valido.')

    if redirect_target and url_has_allowed_host_and_scheme(
        url=redirect_target,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(redirect_target)

    return redirect('post_detail', pk=pk)

like_post = toggle_post_like_view
like_post_ajax = toggle_post_like_ajax_view