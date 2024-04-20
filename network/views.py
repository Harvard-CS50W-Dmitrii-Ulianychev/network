from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.paginator import Paginator

from .models import User, Post, Like
from .forms import PostForm


def index(request):
    if request.method == "POST":
        # If the request method is POST, the user submitted the post form
        form = PostForm(request.POST)
        if form.is_valid():
            form.instance.author = request.user  # Assign the current user as the author of the post
            form.save()
            return redirect("index")
    else:
        # If the request method is GET or the user is not authenticated, render the index page with the post form
        if request.user.is_authenticated:
            # If the user is authenticated, render the index page with the post form
            form = PostForm()  # Create a new instance of the form
        else:
            # If the user is not authenticated, do not render the post form
            form = None
        posts = Post.objects.all().prefetch_related('author').order_by('-created_at')  # Retrieve all posts with the newest first
        paginator = Paginator(posts, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, "network/index.html", {"form": form, "page_obj": page_obj})

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.user != post.author:
        # Return a 403 Forbidden response if the user is not the post's author
        return HttpResponseForbidden()

    if request.method == "POST":
        new_content = request.POST.get("content")
        post.content = new_content
        post.save()

        # Return a JSON response indicating success
        return JsonResponse({"status": "success"})

    # Return a JSON response indicating failure for other request methods
    return JsonResponse({"status": "error"})

from django.shortcuts import get_object_or_404

@login_required
def like_unlike(request):
    if request.method == 'POST':
        post_id = int(request.POST.get('post_id'))
        post = get_object_or_404(Post, pk=post_id)
        user = request.user

        like_obj, created = Like.objects.get_or_create(post=post, user=user)

        if created:
            message = 'liked'
        else:
            like_obj.delete()
            message = 'unliked'

        # Return a JSON response indicating whether the action was successful and the message
        return JsonResponse({'success': True, 'message': message})

    else:
        return JsonResponse({'success': False}, status=405)
    
@login_required
def following(request):
    following_count = request.user.following.count()
    # Get the IDs of the users that the currently logged-in user is following
    following_ids = request.user.following.all().values_list('pk', flat=True)
    # Filter the posts so that only posts from users that the currently logged-in user is following are included
    posts = Post.objects.filter(author_id__in=following_ids).prefetch_related('author').order_by('-created_at')
    return render(request, "network/following.html", {"posts": posts, "following_count": following_count})

def profile(request, user_pk):

    # Retrieve the user object based on the user_pk
    profile_user = get_object_or_404(User, pk=user_pk)

    # Fetch the posts by this user
    posts = Post.objects.filter(author=profile_user).prefetch_related('author').order_by('-created_at')

    # Calculate the count of followers and following for the user
    followers_count = profile_user.followers.count()
    following_count = profile_user.following.count()

    # Pass the user's profile information and posts to the template
    context = {
        "user": request.user,
        "profile_user": profile_user,
        "posts": posts,
        "followers_count": followers_count,
        "following_count": following_count
    }

    return render(request, "network/profile.html", context)

def follow_user(request):
    if request.method == 'POST':

        # Get the ID of the user to follow or unfollow from the POST data
        user_id = request.POST.get('user_id')

        try:
            # Get the user to follow or unfollow
            user_to_follow = get_object_or_404(User, pk=user_id)

            # Get the currently logged-in user
            current_user = request.user

            # Check if the currently logged-in user is already following the user to follow
            if current_user in user_to_follow.followers.all():
                # If the currently logged-in user is already following the user to follow, remove them from the followers list
                user_to_follow.followers.remove(current_user)
                following = False
            else:
                # If the currently logged-in user is not already following the user to follow, add them to the followers list
                user_to_follow.followers.add(current_user)
                following = True

            # Return a JSON response indicating whether the action was successful
            return JsonResponse({'success': True, 'following': following})

        except User.DoesNotExist:
            # If the specified user doesn't exist, return an error response
            return JsonResponse({'success': False, 'error': 'User not found'}, status=404)

    # If the request method is not POST, return a 405 Method Not Allowed response
    else:
        return JsonResponse({'success': False}, status=405)

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
