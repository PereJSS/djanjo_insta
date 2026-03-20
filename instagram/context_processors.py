from profiles.models import UserProfile


def current_user_profile(request):
    if not getattr(request, 'user', None) or not request.user.is_authenticated:
        return {'current_user_profile': None}

    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return {'current_user_profile': profile}