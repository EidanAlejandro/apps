# requests/urls.py
from django.urls import path
from . import views 

requests_urlpatterns = [
    path('', views.main_requests, name='main_requests'),
    path('crear/', views.solicitud_crear, name='solicitud_crear'),
    path('ver/<int:solicitud_id>/', views.solicitud_ver, name='solicitud_ver'),
    path('editar/<int:solicitud_id>/', views.solicitud_editar, name='solicitud_editar'),
    path('eliminar/<int:solicitud_id>/', views.solicitud_eliminar, name='solicitud_eliminar'),
    path('ver/<int:solicitud_id>/responder/<int:pregunta_id>/', views.respuesta_guardar, name='respuesta_guardar'),
    
    # --- NUEVAS URLS SOLICITUD BLOQUEO ---
    path('bloquear/<int:solicitud_id>/', views.solicitud_bloquear, name='solicitud_bloquear'),
    path('bloqueadas/', views.solicitud_list_bloqueadas, name='solicitud_list_bloqueadas'),
    path('desbloquear/<int:solicitud_id>/', views.solicitud_desbloquear, name='solicitud_desbloquear'),

    # --- NUEVA URL PARA SUBIR MULTIMEDIA ---
    path('respuesta/<int:respuesta_id>/subir-multimedia/', views.multimedia_subir, name='multimedia_subir'),
]


