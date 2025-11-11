# users/urls.py
from django.urls import path
from . import views

users_urlpatterns = [
    # URLs para Gestión de Usuarios (Django User + Profile)
    path('', views.user_list, name='user_list'),
    path('ver/<int:user_id>/', views.user_ver, name='user_ver'),
    path('editar/<int:user_id>/', views.user_edit, name='user_edit'),
    path('bloquear/<int:user_id>/', views.user_bloquear, name='user_bloquear'), 
    path('eliminar/<int:user_id>/', views.user_delete, name='user_delete'),
    path('bloqueados/', views.user_list_bloqueados, name='user_list_bloqueados'),
    path('desbloquear/<int:user_id>/', views.user_desbloquear, name='user_desbloquear'),
    path('crear/', views.user_crear, name='user_crear'),

    # URLs para Gestión de Cuadrillas
    path('cuadrillas/', views.cuadrilla_list, name='cuadrilla_list'),
    path('cuadrillas/crear/', views.cuadrilla_crear, name='cuadrilla_crear'),
    path('cuadrillas/ver/<int:cuadrilla_id>/', views.cuadrilla_ver, name='cuadrilla_ver'),
    path('cuadrillas/editar/<int:cuadrilla_id>/', views.cuadrilla_editar, name='cuadrilla_editar'),
    path('cuadrillas/bloquear/<int:cuadrilla_id>/', views.cuadrilla_bloquear, name='cuadrilla_bloquear'),
    path('cuadrillas/eliminar/<int:cuadrilla_id>/', views.cuadrilla_eliminar, name='cuadrilla_eliminar'),
    # --- NUEVAS URLs CUADRILLA BLOQUEO ---
    path('cuadrillas/bloqueadas/', views.cuadrilla_list_bloqueadas, name='cuadrilla_list_bloqueadas'),
    path('cuadrillas/desbloquear/<int:cuadrilla_id>/', views.cuadrilla_desbloquear, name='cuadrilla_desbloquear'),
]