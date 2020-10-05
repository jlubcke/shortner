"""shortner URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import (
    include,
    path,
)

from shortner.views import (
    create,
    delete,
    edit,
    entries,
    go,
    redirect_root,
    ShortnerAdmin,
    submit,
    thanks,
)

urlpatterns = [
    path('', redirect_root),

    path('s/<short>', go),

    path('submit/', submit),
    path('thanks/<short>', thanks),

    path('entries/', entries),
    path('entries/create/', create),
    path('entries/<short>/edit/', edit),
    path('entries/<short>/delete/', delete),

    path('admin/', include(ShortnerAdmin.urls())),
]
