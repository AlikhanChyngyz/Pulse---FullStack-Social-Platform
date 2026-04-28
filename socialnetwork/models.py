from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    # Link each profile to exactly one User
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    # Store the user's bio text
    bio = models.CharField(max_length=500, blank=True)

    # Store uploaded profile image
    profile_picture = models.ImageField(upload_to="profile_pics", blank=True)

    # Users that this user is following
    following = models.ManyToManyField(User, blank=True, related_name="followers")


class Post(models.Model):
    # User who created the post
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    # Content of the post
    text = models.CharField(max_length=280)

    # Timestamp when the post is created
    created_at = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    # User who created the comment
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    # Content of the comment
    text = models.CharField(max_length=280)

    # Timestamp when the comment is created
    created_at = models.DateTimeField(auto_now_add=True)

    # Post that the comment is associated with
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")