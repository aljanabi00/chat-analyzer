from django.contrib.auth import views as auth_views
from django.urls import path

from .views import ChatView, HomeView, MessagesAPIView, register_request


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('chat/<slug:chatname>/', ChatView.as_view(), name='chat'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('signup/', register_request, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('api/messages/<slug:chatname>/', MessagesAPIView.as_view(), name="messages"),
]
