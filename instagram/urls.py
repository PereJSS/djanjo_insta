"""instagram URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from notifications.views import NotificationListView
from posts.views import (
    PostCreateView,
    PostDetailView,
    create_post_comment_view,
    toggle_post_like_ajax_view,
    toggle_post_like_view,
)

from instagram.views import (
    ContactView,
    HomeView,
    LegalView,
    LoginView,
    RegisterView,
    UserProfileDetailView,
    UserProfileListView,
    UserProfileUpdateView,
    logout_user_view,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('legal/', LegalView.as_view(), name='legal'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_user_view, name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('notifications/', NotificationListView.as_view(), name='notification_list'),
    path('profiles/', UserProfileListView.as_view(), name='profiles'),
    path('profile/<int:pk>/', UserProfileDetailView.as_view(), name='profile_detail'),
    path('profile/<int:pk>/edit/', UserProfileUpdateView.as_view(), name='profile_update'),
    path('posts/new/', PostCreateView.as_view(), name='post_create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('posts/<int:pk>/comments/create/', create_post_comment_view, name='post_comment_create'),
    path('posts/<int:pk>/like/', toggle_post_like_view, name='like_post'),
    path('posts/<int:pk>/like/ajax/', toggle_post_like_ajax_view, name='like_post_ajax')
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
