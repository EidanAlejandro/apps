# surveys/urls.py
from django.urls import path
from . import views

surveys_urlpatterns = [
    # URLs Tipo Encuesta
    path('tipos/', views.main_tipo_encuesta, name='main_tipo_encuesta'),
    path('tipos/crear/', views.tipo_encuesta_crear, name='tipo_encuesta_crear'),
    path('tipos/editar/<int:tipo_encuesta_id>/', views.tipo_encuesta_editar, name='tipo_encuesta_editar'),
    path('tipos/eliminar/<int:tipo_encuesta_id>/', views.tipo_encuesta_eliminar, name='tipo_encuesta_eliminar'),

    # URLs Encuesta
    path('encuestas/', views.main_encuesta, name='main_encuesta'),
    path('encuestas/crear/', views.encuesta_crear, name='encuesta_crear'),
    # --- NUEVA URL ENCUESTA VER ---
    path('encuestas/ver/<int:encuesta_id>/', views.encuesta_ver, name='encuesta_ver'),
    path('encuestas/editar/<int:encuesta_id>/', views.encuesta_editar, name='encuesta_editar'),
    path('encuestas/eliminar/<int:encuesta_id>/', views.encuesta_eliminar, name='encuesta_eliminar'),
    # --- NUEVAS URLS ENCUESTA BLOQUEO/DESBLOQUEO ---
    path('encuestas/bloquear/<int:encuesta_id>/', views.encuesta_bloquear, name='encuesta_bloquear'),
    path('encuestas/desbloquear/<int:encuesta_id>/', views.encuesta_desbloquear, name='encuesta_desbloquear'),
    path('encuestas/bloqueadas/', views.encuesta_list_bloqueadas, name='encuesta_list_bloqueadas'),

    # URLs Pregunta (asociadas a una encuesta)
    path('encuestas/<int:encuesta_id>/preguntas/', views.main_pregunta, name='main_pregunta'),
    path('encuestas/<int:encuesta_id>/preguntas/crear/', views.pregunta_crear, name='pregunta_crear'),
    # Editar/Eliminar pregunta usan ID de pregunta
    path('preguntas/editar/<int:pregunta_id>/', views.pregunta_editar, name='pregunta_editar'),
    path('preguntas/eliminar/<int:pregunta_id>/', views.pregunta_eliminar, name='pregunta_eliminar'),
]

