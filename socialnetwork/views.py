from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import LoginForm, RegisterForm, PostForm, ProfileForm
from .models import Post, Profile, Comment
from django.http import HttpResponseForbidden, JsonResponse


def login_action(request):
    # If the user is already logged in, redirect to the global stream
    if request.user.is_authenticated:
        return redirect("global_stream")

    # If the request is a GET request, return the login form
    if request.method == "GET":
        return render(request, "socialnetwork/login.html", {"form": LoginForm()})

    # If the request is a POST request, process the login form
    form = LoginForm(request.POST)

    # If the form is invalid, re-render the login page with error messages and the user-filled form data
    if not form.is_valid():
        return render(request, "socialnetwork/login.html", {"form": form})

    user = authenticate(
        request,
        username=form.cleaned_data["username"],
        password=form.cleaned_data["password"],
    )
    # If the user isn't authenticated, re-render the login page 
    # with an error message and the user-filled form data
    if user is None:
        form.add_error(None, "Invalid username/password.")
        return render(request, "socialnetwork/login.html", {"form": form})

    # If the user is authenticated, log them in
    login(request, user)
    return redirect(reverse("global_stream"))


def register_action(request):
    # If the request is a GET request, return the registration form
    if request.method == "GET":
        return render(request, "socialnetwork/register.html", {"form": RegisterForm()})

    # If the request is a POST request, process the registration form
    form = RegisterForm(request.POST)
    # If the form is invalid, re-render the registration page with error messages and the user-filled form data
    if not form.is_valid():
        return render(request, "socialnetwork/register.html", {"form": form})

    # If the form is valid, create a new user and log them in
    user = User.objects.create_user(
        username=form.cleaned_data["username"],
        password=form.cleaned_data["password"],
        email=form.cleaned_data["email"],
        first_name=form.cleaned_data["first_name"],
        last_name=form.cleaned_data["last_name"],
    )
    login(request, user)
    return redirect(reverse("global_stream"))


def logout_action(request):
    # Log the user out
    logout(request)
    return redirect(reverse("login"))


@login_required
def global_stream(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            return redirect("global_stream")
    else:
        form = PostForm()

    posts = Post.objects.all().order_by("-created_at", "-id")
    return render(request, "socialnetwork/global.html", {
        "posts": posts,
        "form": form
    })


@login_required
def follower_stream(request):
    profile = Profile.objects.get_or_create(user=request.user)[0]

    followed_users = profile.following.all()
    posts = Post.objects.filter(author__in=followed_users).order_by("-created_at", "-id")

    return render(request, "socialnetwork/follower.html", {
        "posts": posts
    })


@login_required
def my_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("my_profile")
    else:
        form = ProfileForm(instance=profile)

    return render(request, "socialnetwork/myprofile.html", {
        "form": form,
        "profile": profile,
    })


@login_required
def other_profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = Profile.objects.get_or_create(user=user)[0]
    posts = Post.objects.filter(author=user).order_by("-created_at")

    return render(request, "socialnetwork/otherprofile.html", {
        "profile_user": user,
        "profile": profile,
        "posts": posts,
    })


@login_required
def follow(request, username):
    target_user = get_object_or_404(User, username=username)

    if target_user == request.user:
        return HttpResponseForbidden()

    profile = Profile.objects.get_or_create(user=request.user)[0]
    profile.following.add(target_user)

    return redirect("other_profile", username=username)


@login_required
def unfollow(request, username):
    target_user = get_object_or_404(User, username=username)

    profile = Profile.objects.get_or_create(user=request.user)[0]
    profile.following.remove(target_user)

    return redirect("other_profile", username=username)


def get_global(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    if request.method != "GET":
        return JsonResponse({"error": "Invalid method"}, status=405)

    all_posts = Post.objects.all().order_by("-created_at", "-id")

    posts = []
    for p in all_posts:
        all_comments = p.comments.all().order_by("created_at", "id")

        comments = []
        for c in all_comments:
            comments.append({
                "id": c.id,
                "text": c.text,
                "created_at": c.created_at.isoformat(),
                "author_username": c.author.username,
                "author_first_name": c.author.first_name,
                "author_last_name": c.author.last_name,
                "post_id": p.id,
            })

        posts.append({
            "id": p.id,
            "text": p.text,
            "created_at": p.created_at.isoformat(),
            "author_username": p.author.username,
            "author_first_name": p.author.first_name,
            "author_last_name": p.author.last_name,
            "comments": comments,
        })

    return JsonResponse({"posts": posts}, status=200)


def add_comment(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    comment_text = request.POST.get("comment_text", "").strip()
    post_id = request.POST.get("post_id", "").strip()

    if not comment_text:
        return JsonResponse({"error": "Missing comment_text"}, status=400)

    if not post_id.isdigit():
        return JsonResponse({"error": "Invalid post_id"}, status=400)

    try:
        post = Post.objects.get(id=int(post_id))
    except Post.DoesNotExist:
        return JsonResponse({"error": "Invalid post_id"}, status=400)

    comment = Comment.objects.create(
        author=request.user,
        text=comment_text,
        post=post
    )

    return JsonResponse({
        "comment": {
            "id": comment.id,
            "text": comment.text,
            "created_at": comment.created_at.isoformat(),
            "author_username": comment.author.username,
            "author_first_name": comment.author.first_name,
            "author_last_name": comment.author.last_name,
            "post_id": post.id,
        }
    }, status=200)


@login_required
def get_follower(request):
    if request.method != "GET":
        return JsonResponse({"error": "Invalid method"}, status=405)

    profile = Profile.objects.get_or_create(user=request.user)[0]
    followed_users = profile.following.all()

    all_posts = Post.objects.filter(author__in=followed_users).order_by("-created_at", "-id")

    posts = []
    for p in all_posts:
        comments_qs = Comment.objects.filter(post=p).order_by("created_at", "id")

        comments = []
        for c in comments_qs:
            comments.append({
                "id": c.id,
                "text": c.text,
                "created_at": c.created_at.isoformat(),
                "author_username": c.author.username,
                "author_first_name": c.author.first_name,
                "author_last_name": c.author.last_name,
                "post_id": p.id,
            })

        posts.append({
            "id": p.id,
            "text": p.text,
            "created_at": p.created_at.isoformat(),
            "author_username": p.author.username,
            "author_first_name": p.author.first_name,
            "author_last_name": p.author.last_name,
            "comments": comments,
        })

    return JsonResponse({"posts": posts}, status=200)