from django.contrib import admin
from django.urls import path
from socialnetwork import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", views.login_action, name="login"),
    path("register", views.register_action, name="register"),
    path("logout", views.logout_action, name="logout"),

    path("global", views.global_stream, name="global_stream"),
    path('follower', views.follower_stream, name='follower_stream'),
    path('profile', views.my_profile, name='my_profile'),
    path('profile/<str:username>', views.other_profile, name='other_profile'),

    path("profile/<str:username>/follow", views.follow, name="follow"),
    path("profile/<str:username>/unfollow", views.unfollow, name="unfollow"),
    path("socialnetwork/get-global", views.get_global, name="get_global"),
    path("socialnetwork/add-comment", views.add_comment, name="add_comment"),
    path("socialnetwork/get-follower", views.get_follower, name="get_follower"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
