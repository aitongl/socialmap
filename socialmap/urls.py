from django.urls import path
from socialmap import views

urlpatterns = [
    path('login/', views.login_action, name='login'),
    path('register/', views.register_action, name='register'),
    path('profile/', views.profile_action, name='profile'),
    path('other/<int:id>', views.profile_view, name='other'),
    path('photo/<int:id>', views.get_photo, name='photo'),
    path('follow/<int:id>', views.follow, name='follow'),
    path('unfollow/<int:id>', views.unfollow, name='unfollow'),
    path('messages/', views.profile_action, name='messages'),
    path('', views.map_view, name='map_view'),
    path('update_location/', views.update_location, name='update_location')
]