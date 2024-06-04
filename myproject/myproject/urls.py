"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from accounts.views import signup, user_login,send_contact_email
from accounts.views import home
from accounts.views import save_chat, get_saved_chats, generate_text

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', signup),
    path('login/', user_login), 
    path('send_contact_email/', send_contact_email, name='send_contact_email'),
    path('api/save_chat/', save_chat, name='save_chat'),
    path('api/get_saved_chats/', get_saved_chats, name='get_saved_chats'),
    path('generate_text/', generate_text, name='generate_text'),
    path('', home, name='home'),  # Add the root path
    
    
]
