from django.contrib import admin
from django.urls import path
from chatbot.views import *
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', chat_view, name='chat_view'),  # The home page, which handles the chat

]