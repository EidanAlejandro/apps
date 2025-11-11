# users/models.py
from django.db import models
from django.contrib.auth.models import User
# Importar Departamento usando string para evitar importación circular
from organization.models import Departamento 

# Modelo Cuadrilla (vinculado a Departamento y a un User como Jefe)
class Cuadrilla(models.Model):
    id_cuadrilla = models.AutoField(primary_key=True)
    nombre_cuadrilla = models.CharField(max_length=100, default='') 
    departamento = models.ForeignKey('organization.Departamento', on_delete=models.CASCADE, related_name='cuadrilla') 
    
    # --- CAMBIOS AQUÍ ---
    jefe = models.ForeignKey(
        User, 
        related_name='cuadrillas_lideradas', 
        # Quitar null=True y blank=True para hacerlo obligatorio
        # null=True, 
        # blank=True,
        # Cambiar on_delete a PROTECT para evitar borrar jefes asignados
        on_delete=models.PROTECT, 
    )
    # --- FIN CAMBIOS ---

    state = models.CharField(max_length=20, default='Activo')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        dep_nombre = self.departamento.nombre_departamento if self.departamento else 'Sin Depto.'
        return f"{self.nombre_cuadrilla} ({dep_nombre})"
