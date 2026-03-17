from django.views.generic.edit import CreateView
from posts.models import Post
from posts.forms import PostCreateForm
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.detail import DetailView
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST

@method_decorator(login_required, name='dispatch')
class PostCreateView(CreateView):
    model = Post
    template_name = 'posts/post_create.html'
    form_class = PostCreateForm
    success_url = reverse_lazy('home')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.add_message(self.request, messages.SUCCESS, 'Publicación creada correctamente.')
        return super(PostCreateView, self).form_valid(form)


@method_decorator(login_required, name='dispatch')
class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'
    

@login_required    
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        messages.add_message(request, messages.SUCCESS, 'Has dejado de dar me gusta a esta publicación.')
    else:
        post.likes.add(request.user)
        messages.add_message(request, messages.SUCCESS, 'Has dado me gusta a esta publicación.')
    return redirect('post_detail', pk=pk)

@login_required
@require_POST
def like_post_ajax(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
        message = 'Has dejado de dar me gusta a esta publicación.'
    else:
        post.likes.add(request.user)
        liked = True
        message = 'Has dado me gusta a esta publicación.'
    return JsonResponse({'liked': liked, 'likes_count': post.likes.count(), 'message': message})