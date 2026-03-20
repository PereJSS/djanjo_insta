from django.core.exceptions import ObjectDoesNotExist
from django.db.models import BooleanField, Count, Exists, OuterRef, Value
from django.urls import reverse

from notifications.models import Notification
from posts.models import Post


def get_posts_queryset_for_display(posts_queryset, current_user):
    """Annotate posts with presentation-friendly fields used by templates."""
    posts_with_engagement_data = posts_queryset.select_related("user", "user__profile").prefetch_related(
        "comments__user"
    ).annotate(
        total_likes=Count("likes", distinct=True),
        total_comments=Count("comments", distinct=True),
    )

    if getattr(current_user, "is_authenticated", False):
        like_through_model = Post.likes.through
        return posts_with_engagement_data.annotate(
            is_liked_by_current_user=Exists(
                like_through_model.objects.filter(post_id=OuterRef("pk"), user_id=current_user.pk)
            )
        )

    return posts_with_engagement_data.annotate(
        is_liked_by_current_user=Value(False, output_field=BooleanField())
    )


def get_home_feed_posts(current_user, limit=10):
    """Return recent posts for the home feed with display annotations."""
    if getattr(current_user, "is_authenticated", False):
        try:
            following_profiles = current_user.profile.following.all()
            feed_queryset = Post.objects.filter(user__profile__in=following_profiles)
        except ObjectDoesNotExist:
            feed_queryset = Post.objects.all()
    else:
        feed_queryset = Post.objects.all()

    ordered_feed_queryset = feed_queryset.order_by("-created_at")
    return get_posts_queryset_for_display(ordered_feed_queryset, current_user)[:limit]


def toggle_post_like_for_user(post, acting_user):
    """Toggle like status for a post and return the resulting like state."""
    user_already_liked_post = post.likes.filter(pk=acting_user.pk).exists()

    if user_already_liked_post:
        post.likes.remove(acting_user)
        return False

    post.likes.add(acting_user)

    if post.user_id != acting_user.id:
        Notification.objects.create(
            recipient=post.user,
            actor=acting_user,
            notification_type=Notification.TYPE_LIKE,
            message=f"A {acting_user.username} le ha gustado tu publicación.",
            target_url=reverse("post_detail", kwargs={"pk": post.pk}),
        )

    return True


def build_like_toggle_message(user_liked_post):
    if user_liked_post:
        return "Has dado me gusta a esta publicación."
    return "Has dejado de dar me gusta a esta publicación."
