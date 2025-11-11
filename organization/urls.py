from django.urls import path
from . import views

organization_urlpatterns = [
    # Direccion
    path('direcciones/', views.main_direccion, name='main_direccion'),
    path('direcciones/crear/', views.direccion_crear, name='direccion_crear'),
    path('direcciones/guardar/', views.direccion_guardar, name='direccion_guardar'),
    path('direcciones/ver/<int:direccion_id>/', views.direccion_ver, name='direccion_ver'),
    path('direcciones/editar/<int:direccion_id>/', views.direccion_editar, name='direccion_editar'),
    path('direcciones/actualizar/', views.direccion_actualizar, name='direccion_actualizar'),
    path('direcciones/bloquear/<int:direccion_id>/', views.direccion_bloquea, name='direccion_bloquea'),
    path('direcciones/eliminar/<int:direccion_id>/', views.direccion_elimina, name='direccion_elimina'),
    # Nuevas URLs Direccion Bloqueo/Desbloqueo
    path('direcciones/bloqueadas/', views.direccion_list_bloqueadas, name='direccion_list_bloqueadas'),
    path('direcciones/desbloquear/<int:direccion_id>/', views.direccion_desbloquear, name='direccion_desbloquear'),

    # Departamento
    path('departamentos/', views.main_departamento, name='main_departamento'),
    path('departamentos/crear/', views.departamento_crear, name='departamento_crear'),
    path('departamentos/ver/<int:departamento_id>/', views.departamento_ver, name='departamento_ver'),
    path('departamentos/editar/<int:departamento_id>/', views.departamento_editar, name='departamento_editar'),
    path('departamentos/bloquear/<int:departamento_id>/', views.departamento_bloquea, name='departamento_bloquea'),
    path('departamentos/eliminar/<int:departamento_id>/', views.departamento_elimina, name='departamento_elimina'),
    # Nuevas URLs Departamento Bloqueo/Desbloqueo
    path('departamentos/bloqueados/', views.departamento_list_bloqueados, name='departamento_list_bloqueados'),
    path('departamentos/desbloquear/<int:departamento_id>/', views.departamento_desbloquear, name='departamento_desbloquear'),
]

