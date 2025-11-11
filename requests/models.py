# requests/models.py

from django.db import models
# Imports correctos: apuntan a User de Django y a modelos de surveys
from surveys.models import Encuesta, Pregunta 
from django.contrib.auth.models import User # Importar User de Django

class EstadoSolicitud(models.Model):
    id_estado = models.AutoField(primary_key=True)
    nombre_estado = models.CharField(max_length=50, unique=True)
    state = models.CharField(max_length=20, default='Activo')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nombre_estado

class Solicitud(models.Model):
    id_solicitud = models.AutoField(primary_key=True)
    id_encuesta = models.ForeignKey('surveys.Encuesta', on_delete=models.CASCADE)
    # Correcto: Apuntan a User con related_name
    id_territorial = models.ForeignKey(User, related_name='solicitudes_territorial', on_delete=models.CASCADE) 
    # --- CORRECCIÓN AQUÍ ---
    # ForeignKey debe apuntar al modelo Cuadrilla
    id_cuadrilla = models.ForeignKey(
        'users.Cuadrilla', # Apunta al modelo Cuadrilla
        related_name='solicitudes_asignadas', 
        on_delete=models.SET_NULL, # Si se borra la Cuadrilla, la solicitud queda sin asignar
        null=True, 
        blank=True
    )
    # --- FIN CORRECCIÓN ---
    id_estado = models.ForeignKey('EstadoSolicitud', on_delete=models.CASCADE)
    
    titulo = models.CharField(max_length=200, default='Sin título')
    descripcion = models.TextField(blank=True, null=True)
    ubicacion = models.CharField(max_length=300, blank=True, null=True)
    prioridad = models.CharField(max_length=20, choices=[
        ('baja', 'Baja'),
        ('normal', 'Normal'), 
        ('alta', 'Alta')
    ], default='normal')
    
    state = models.CharField(max_length=20, default='Activo')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Solicitud {self.id_solicitud} - {self.titulo}"

class Respuesta(models.Model):
    id_respuesta = models.AutoField(primary_key=True)
    id_pregunta = models.ForeignKey('surveys.Pregunta', on_delete=models.CASCADE)
    id_solicitud = models.ForeignKey('Solicitud', on_delete=models.CASCADE)
    respuesta = models.TextField()
    state = models.CharField(max_length=20, default='Activo')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Respuesta {self.id_respuesta}"

class Multimedia(models.Model):
    TIPOS_MULTIMEDIA = [
        ('imagen', 'Imagen'),
        ('video', 'Video'),
        ('audio', 'Audio'),
    ]
    id_multimedia = models.AutoField(primary_key=True)
    id_respuesta = models.ForeignKey('Respuesta', on_delete=models.CASCADE, null=True, blank=True)
    id_solicitud = models.ForeignKey('Solicitud', on_delete=models.CASCADE, null=True, blank=True)
    tipo = models.CharField(max_length=20, choices=TIPOS_MULTIMEDIA)
    archivo = models.FileField(upload_to='multimedia/')
    descripcion = models.CharField(max_length=200, blank=True, null=True)
    state = models.CharField(max_length=20, default='Activo')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Multimedia {self.id_multimedia} - {self.tipo}"