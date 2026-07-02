"""
URL configuration for setup project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path
from pet.views import cadastrar_animal, listar_animais, editar_animal, adotar_animal, index, excluir_animal, login_usuario, logout_usuario, sobre_nos, como_ajudar
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('animais/cadastrar/', cadastrar_animal, name='cadastrar_animal'),
    path('animais/listar/', listar_animais, name='listar_animais'),
    path('animais/editar/<int:id>/', editar_animal, name='editar_animal'),
    path('animais/adotar/<int:id>/', adotar_animal, name="adotar_animal"),
    path('animais/excluir/<int:id>/', excluir_animal, name='excluir_animal'),
    path("login/", login_usuario, name="login"),
    path("logout/", logout_usuario, name="logout"),
    path('sobre/', sobre_nos, name='sobre_nos'),
    path('comoajudar/', como_ajudar, name='como_ajudar'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )