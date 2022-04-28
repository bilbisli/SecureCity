"""SecureCity URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path, re_path, include
from HomePage import views as HomePageV
from Authentication import views as AuthenticationV
from AdminRequest import views as AdminRequestV
from Contact import views as ContactV
from Patrols import views as PatrolsV
from adminPage import views as AdminV

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomePageV.home, name="homepage"),
    path('CreateContact/', ContactV.createContact, name='CreateContact'),
    path('AddParent/', AuthenticationV.AddParent, name="AddParent"),
    path('Login/', AuthenticationV.loginU, name="Login"),
    path('logout/', AuthenticationV.logoutuser, name="logoutuser"),
    path('adminPage/', AdminV.adminP, name="adminPage"),
    path('adminEdit/', AdminV.adminEdit, name="adminEdit"),
    path('adminDelete/', AdminV.adminDelete, name="adminDelete"),
    path(r'ContactManagement/', ContactV.contact_management, name='ContactManagement'),
    path('mypage/', AuthenticationV.residentPage, name='resident_page'),
    path('becomePatrolManager/', AdminRequestV.becomePatrolManager, name='becomePatrolManager'),
    path('CreateRequest/', AdminRequestV.CreateRequest, name='CreateRequest'),
    path('updateDatabases/', AdminV.updateDatabases, name='updateDatabases'),
    re_path('patrols/', include('Patrols.urls'), name='patrols'),
]
