from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from .forms import RegistrationForm,LoginForm
from django.contrib import messages
from django.views.generic.edit import FormView
from django.contrib.auth import authenticate, login, logout 
from django.http import HttpResponseRedirect
from django.views.generic import DetailView
from profiles.models import UserProfile, Follow
from django.views.generic.edit import UpdateView
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from posts.models import Post
from django.views.generic import ListView
from .forms import FollowForm

# Create your views here.

class HomeView(TemplateView):
    template_name = 'general/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            following_profiles = self.request.user.profile.following.all()
            last_posts = Post.objects.filter(user__profile__in=following_profiles).order_by('-created_at')[:10]
            context['posts'] = last_posts
        else:
            last_posts = Post.objects.all().order_by('-created_at')[:10]
        context['last_posts'] = last_posts
        return context

class LegalView(TemplateView):
    template_name = 'general/legal.html'


class LoginView(FormView):
    template_name = 'general/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        usuario = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=usuario, password=password)
        if user is not None:
            login(self.request, user)
            messages.add_message(self.request, messages.SUCCESS, f'Bienvenido {user.username}')
            return HttpResponseRedirect(reverse_lazy('home'))
        else:
            messages.add_message(self.request, messages.ERROR, 'Usuario o contraseña incorrectos.')
            return self.form_invalid(form)
        
class RegisterView(CreateView):
    template_name = 'general/register.html'
    model = User
    success_url = reverse_lazy('login')
    form_class = RegistrationForm

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Usuario registrado correctamente.')
        return super(RegisterView, self).form_valid(form)

class ContactView(TemplateView):
    template_name = 'general/contact.html'


@login_required
def logout_view(request):
    logout(request)
    messages.add_message(request, messages.SUCCESS, 'Has cerrado sesión correctamente.')
    return HttpResponseRedirect(reverse_lazy('home'))

@method_decorator(login_required, name='dispatch')
class ProfileDetailView(DetailView, FormView):
    model = UserProfile
    template_name = 'general/profile_detail.html'
    context_object_name = 'profile'
    form_class = FollowForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_obj = context.get('profile') or self.get_object()
        context['is_following'] = Follow.objects.filter(
            follower=self.request.user.profile,
            following=profile_obj,
        ).exists()
        return context
    
    def form_valid(self, form):
        usuario_a_seguir_pk = form.cleaned_data['profile_pk']
        usuario_a_seguir_perfil = UserProfile.objects.get(pk=usuario_a_seguir_pk)
        action = form.cleaned_data.get('action') or 'follow'

        if usuario_a_seguir_perfil == self.request.user.profile:
            messages.add_message(self.request, messages.ERROR, 'No puedes seguirte a ti mismo egocentrico.')
            return HttpResponseRedirect(reverse('profile_detail', kwargs={'pk': self.get_object().pk}))

        if action == 'unfollow':
            self.request.user.profile.unfollow(usuario_a_seguir_perfil)
            messages.add_message(self.request, messages.SUCCESS, f'Has dejado de seguir a {usuario_a_seguir_perfil.user.username}.')
        else:
            self.request.user.profile.follow(usuario_a_seguir_perfil)
            messages.add_message(self.request, messages.SUCCESS, f'Ahora sigues a {usuario_a_seguir_perfil.user.username}.')
        return HttpResponseRedirect(reverse('profile_detail', kwargs={'pk': self.get_object().pk}))
        
    
    
@method_decorator(login_required, name='dispatch')
class ProfileListView(ListView):
    model = UserProfile
    template_name = 'general/profile_list.html'
    context_object_name = 'profiles'
    def get_queryset(self):
        return UserProfile.objects.exclude(user=self.request.user)
       
@method_decorator(login_required, name='dispatch')
class ProfileUpdateView(UpdateView):
    model = UserProfile
    template_name = 'general/profile_update.html'
    context_object_name = 'profile'
    fields = ['bio', 'birth_date', 'profile_picture']
    
    def dispatch(self, request, *args, **kwargs):
        user_profile = self.get_object()
        if user_profile.user != request.user:
            messages.add_message(request, messages.ERROR, 'No tienes permiso para editar este perfil.')
            return HttpResponseRedirect(reverse_lazy('home'))
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Perfil actualizado correctamente.')
        return super(ProfileUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('profile_detail', kwargs={'pk': self.object.pk})

    
    