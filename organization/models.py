# organization/models.py
from django.db import models
from django.contrib.auth.models import User # Importar User de Django

class Direccion(models.Model):
    id_direccion = models.AutoField(primary_key=True)
    # Cambiar ForeignKey para apuntar a User de Django
    usuario = models.ForeignKey(User, on_delete=models.CASCADE) 
    nombre_direccion = models.CharField(max_length=200)
    state = models.CharField(max_length=20, default='Activo')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nombre_direccion
    
class Departamento(models.Model):
    id_departamento = models.AutoField(primary_key=True)
    id_direccion = models.ForeignKey(Direccion, on_delete=models.CASCADE)
     # Cambiar ForeignKey para apuntar a User de Django
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre_departamento = models.CharField(max_length=50, null=False, blank=False)
    state = models.CharField(max_length=20, default='Activo')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre_departamento