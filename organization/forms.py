# organization/forms.py
from django import forms
from .models import Departamento
from django.contrib.auth.models import User, Group # Import User and Group

class DepartamentoForm(forms.ModelForm):
    # Sobrescribir el campo 'usuario' (renombrado de id_usuario) para filtrar
    usuario = forms.ModelChoiceField(
        queryset=User.objects.filter(
            is_active=True, 
            # Filtra por el nombre del grupo asignado en el Profile
            profile__group__name='Departamento' 
        ),
        label="Encargado (Departamento)" # Etiqueta más clara
    )
    
    class Meta:
        model = Departamento
        # Asegúrate de usar 'usuario' si renombraste el campo en models.py
        fields = ['nombre_departamento', 'id_direccion', 'usuario'] 
        widgets = { # Opcional: añadir clases para estilos si usas Bootstrap
            'nombre_departamento': forms.TextInput(attrs={'class': 'form-control'}),
            'id_direccion': forms.Select(attrs={'class': 'form-select'}),
            'usuario': forms.Select(attrs={'class': 'form-select'}),
        }