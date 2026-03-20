from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView, FormView, UpdateView

from posts.services import get_home_feed_posts, get_posts_queryset_for_display
from profiles.models import UserProfile
from profiles.services import (
    get_user_profile_detail_queryset,
    get_user_profiles_for_listing,
    process_follow_action_request,
)

from .forms import FollowForm, LoginForm, RegistrationForm

class HomeView(TemplateView):
    template_name = 'general/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['last_posts'] = get_home_feed_posts(self.request.user, limit=10)
        return context

class LegalView(TemplateView):
    template_name = 'general/legal.html'


class LoginView(FormView):
    template_name = 'general/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        username_value = form.cleaned_data['username']
        password_value = form.cleaned_data['password']
        authenticated_user = authenticate(username=username_value, password=password_value)
        if authenticated_user is not None:
            login(self.request, authenticated_user)
            messages.add_message(self.request, messages.SUCCESS, f'Bienvenido {authenticated_user.username}')
            return HttpResponseRedirect(reverse_lazy('home'))

        messages.add_message(self.request, messages.ERROR, 'Usuario o contraseña incorrectos.')
        return self.form_invalid(form)
        
class RegisterView(CreateView):
    template_name = 'general/register.html'
    model = User
    success_url = reverse_lazy('login')
    form_class = RegistrationForm

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Usuario registrado correctamente.')
        return super().form_valid(form)

class ContactView(TemplateView):
    template_name = 'general/contact.html'


@login_required
def logout_user_view(request):
    logout(request)
    messages.add_message(request, messages.SUCCESS, 'Has cerrado sesión correctamente.')
    return HttpResponseRedirect(reverse_lazy('home'))

@method_decorator(login_required, name='dispatch')
class UserProfileDetailView(DetailView, FormView):
    model = UserProfile
    template_name = 'general/profile_detail.html'
    context_object_name = 'profile'
    form_class = FollowForm

    def get_queryset(self):
        return get_user_profile_detail_queryset(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        viewed_profile = context.get('profile') or self.get_object()
        context['is_following'] = getattr(viewed_profile, 'is_followed_by_current_user', False)
        context['is_own_profile'] = viewed_profile.user_id == self.request.user.id
        profile_posts_queryset = viewed_profile.user.posts.all().order_by('-created_at')
        context['profile_posts'] = get_posts_queryset_for_display(profile_posts_queryset, self.request.user)
        return context

    def form_valid(self, form):
        target_profile = self.get_object()
        requested_follow_action = form.cleaned_data.get('follow_action') or 'follow'
        follow_action_result = process_follow_action_request(
            acting_user=self.request.user,
            target_profile=target_profile,
            requested_action=requested_follow_action,
        )

        message_level = messages.SUCCESS if follow_action_result.was_successful else messages.ERROR
        messages.add_message(self.request, message_level, follow_action_result.feedback_message)
        return HttpResponseRedirect(reverse('profile_detail', kwargs={'pk': target_profile.pk}))


@method_decorator(login_required, name='dispatch')
class UserProfileListView(ListView):
    model = UserProfile
    template_name = 'general/profile_list.html'
    context_object_name = 'profiles'

    def get_queryset(self):
        return get_user_profiles_for_listing(self.request.user)


@method_decorator(login_required, name='dispatch')
class UserProfileUpdateView(UpdateView):
    model = UserProfile
    template_name = 'general/profile_update.html'
    context_object_name = 'profile'
    fields = ['bio', 'birth_date', 'profile_picture']

    def dispatch(self, request, *args, **kwargs):
        editable_profile = self.get_object()
        if editable_profile.user != request.user:
            messages.add_message(request, messages.ERROR, 'No tienes permiso para editar este perfil.')
            return HttpResponseRedirect(reverse_lazy('home'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Perfil actualizado correctamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('profile_detail', kwargs={'pk': self.object.pk})

logout_view = logout_user_view
ProfileDetailView = UserProfileDetailView
ProfileListView = UserProfileListView
ProfileUpdateView = UserProfileUpdateView


    

    