# requests/forms.py
from django import forms
from .models import Solicitud, Respuesta, EstadoSolicitud 
from users.models import Cuadrilla# Importar EstadoSolicitud
from django.contrib.auth.models import User, Group # Importar User y Group
from surveys.models import Encuesta # Importar Encuesta
from .models import Multimedia

class SolicitudForm(forms.ModelForm):
    # Definir explícitamente los campos ForeignKey para filtrar por rol/grupo
    id_territorial = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True, profile__group__name='Territorial'), # Filtra User por Grupo 'Territorial'
        label="Territorial Asignado",
        empty_label="Seleccione un territorial",
        widget=forms.Select(attrs={'class': 'form-select'}) # Opcional: Estilo Bootstrap
    )
    
    # --- CORRECCIÓN AQUÍ ---
    id_cuadrilla = forms.ModelChoiceField(
        queryset=Cuadrilla.objects.filter(state='Activo'), # Busca en el modelo Cuadrilla
        label="Cuadrilla Asignada",
        empty_label="Seleccione una cuadrilla (Opcional)",
        required=False, 
        widget=forms.Select(attrs={'class': 'form-select'}) 
    )
    # --- FIN CORRECCIÓN ---
    
    
    # También definir los otros Selects para asegurar filtros y etiquetas
    id_encuesta = forms.ModelChoiceField(
        queryset=Encuesta.objects.filter(state='Activo'),
        label="Tipo de Encuesta",
        empty_label="Seleccione una encuesta",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    id_estado = forms.ModelChoiceField(
        queryset=EstadoSolicitud.objects.filter(state='Activo'),
        label="Estado",
        empty_label="Seleccione un estado",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Solicitud
        # Lista completa de campos que el formulario manejará
        fields = [
            'titulo', 'descripcion', 'id_encuesta', 'id_territorial', 
            'ubicacion', 'prioridad', 'id_estado', 'id_cuadrilla' 
        ]
        # Widgets para mejorar apariencia (Bootstrap opcional)
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'prioridad': forms.Select(attrs={'class': 'form-select'}),
            # Los widgets para los ForeignKey ya se definieron arriba
        }

class RespuestaForm(forms.ModelForm):
    class Meta:
        model = Respuesta
        fields = ['respuesta']
        widgets = {
            'respuesta': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Escribe tu respuesta aquí...', 'class': 'form-control'}),
        }

class MultimediaForm(forms.ModelForm):
    class Meta:
        model = Multimedia
        # Campos que pediremos al subir
        fields = ['tipo', 'archivo', 'descripcion'] 
        widgets = { # Opcional: Estilos
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'archivo': forms.FileInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }