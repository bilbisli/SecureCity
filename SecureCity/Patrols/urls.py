from django.urls import path, include
from .views import *


urlpatterns = [
    path('patrol/<int:patrol_id>/', patrol_page, name='patrol_page'),
    path('', parent_patrol, name='parent_patrol'),
    path(r'PatrolManagement/', patrol_management, name='PatrolManagement'),
    path(r'PatrolManagement/CreatePatrol', create_patrol, name='CreatePatrol'),
]