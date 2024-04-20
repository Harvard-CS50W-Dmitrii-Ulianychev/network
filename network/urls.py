
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("profile/<str:user_pk>", views.profile, name="profile"),
    path("edit-post/<int:post_id>", views.edit_post, name="edit_post"),
    path("like-unlike", views.like_unlike, name="like_unlike"),
    path("follow", views.follow_user, name="follow"),
    path("following", views.following, name="following"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register")
]
