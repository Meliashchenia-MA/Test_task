from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views
from .views import profile_view, login_view, reg_view, logout_view, upload_file
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home_view, name="home"),
    path('login', views.login_view, name="login"),
    path('reg', views.reg_view, name="registration"),
    path('profile', views.profile_view, name="profile"),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('upload/', views.upload_file, name='upload_file'),
    path('download/<int:id>/<str:format>/', views.download_image, name='download_image'),
    path('display/<int:id>/', views.display_image, name='display_image'),
]

