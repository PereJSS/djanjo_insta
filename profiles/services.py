from dataclasses import dataclass

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import BooleanField, Count, Exists, OuterRef, Value
from django.urls import reverse

from notifications.models import Notification
from profiles.models import Follow, UserProfile


@dataclass(frozen=True)
class FollowActionResult:
    was_successful: bool
    feedback_message: str


def get_user_profiles_for_listing(excluded_user):
    return (
        UserProfile.objects.exclude(user=excluded_user)
        .select_related("user")
        .annotate(
            followers_count=Count("followers", distinct=True),
            following_count=Count("following", distinct=True),
        )
    )


def get_user_profile_detail_queryset(current_user):
    profile_detail_queryset = UserProfile.objects.select_related("user").annotate(
        followers_count=Count("followers", distinct=True),
        following_count=Count("following", distinct=True),
    )

    if getattr(current_user, "is_authenticated", False):
        try:
            current_user_profile = current_user.profile
            return profile_detail_queryset.annotate(
                is_followed_by_current_user=Exists(
                    Follow.objects.filter(follower=current_user_profile, following=OuterRef("pk"))
                )
            )
        except ObjectDoesNotExist:
            pass

    return profile_detail_queryset.annotate(
        is_followed_by_current_user=Value(False, output_field=BooleanField())
    )


def process_follow_action_request(acting_user, target_profile, requested_action):
    """Apply follow/unfollow action with domain-level validations."""
    try:
        acting_user_profile = acting_user.profile
    except ObjectDoesNotExist:
        return FollowActionResult(
            was_successful=False,
            feedback_message="No se pudo obtener tu perfil para procesar esta acción.",
        )

    if target_profile == acting_user_profile:
        return FollowActionResult(
            was_successful=False,
            feedback_message="No puedes seguirte a ti mismo.",
        )

    normalized_action = requested_action if requested_action in {"follow", "unfollow"} else "follow"

    if normalized_action == "unfollow":
        was_following = acting_user_profile.unfollow(target_profile)
        return FollowActionResult(
            was_successful=True,
            feedback_message=(
                f"Has dejado de seguir a {target_profile.user.username}."
                if was_following
                else f"No seguías a {target_profile.user.username}."
            ),
        )

    follow_was_created = acting_user_profile.follow(target_profile)

    if follow_was_created:
        Notification.objects.create(
            recipient=target_profile.user,
            actor=acting_user,
            notification_type=Notification.TYPE_FOLLOW,
            message=f"{acting_user.username} ha empezado a seguirte.",
            target_url=reverse("profile_detail", kwargs={"pk": acting_user_profile.pk}),
        )

    return FollowActionResult(
        was_successful=True,
        feedback_message=(
            f"Ahora sigues a {target_profile.user.username}."
            if follow_was_created
            else f"Ya seguías a {target_profile.user.username}."
        ),
    )
