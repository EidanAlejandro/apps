# users/forms.py
from django import forms
from registration.models import Profile 
from django.contrib.auth.models import User, Group
from .models import Cuadrilla 
from organization.models import Departamento
from django.contrib.auth.forms import UserCreationForm


class UserProfileForm(forms.ModelForm):
    # Campos del User que queremos editar
    first_name = forms.CharField(label="Nombre", required=True)
    last_name = forms.CharField(label="Apellido", required=True)
    email = forms.EmailField(label="Correo", required=True)

    # Campo para elegir el Grupo (Rol)
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(), 
        label="Rol / Perfil", 
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}) # Estilo opcional
    )
    # Campo para el teléfono (del Profile)
    phone = forms.CharField(label="Teléfono", required=False, widget=forms.TextInput(attrs={'class': 'form-control'})) # Estilo opcional

    class Meta:
        model = User # El formulario principal edita el User
        fields = ['first_name', 'last_name', 'email']
        # Añadir widgets para Bootstrap si se desea
        widgets = {
             'first_name': forms.TextInput(attrs={'class': 'form-control'}),
             'last_name': forms.TextInput(attrs={'class': 'form-control'}),
             'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si estamos editando (instance tiene datos), precargamos los campos de Profile
        if self.instance and self.instance.pk:
            try:
                # Usamos select_related para optimizar la consulta
                profile = Profile.objects.select_related('group').get(user=self.instance)
                self.fields['group'].initial = profile.group
                self.fields['phone'].initial = profile.phone
            except Profile.DoesNotExist:
                pass # Si no tiene profile, los campos quedan vacíos

    def save(self, commit=True):
        # Guardamos el User primero
        user = super().save(commit=commit)
        # Luego, obtenemos o creamos el Profile y actualizamos sus datos
        profile, created = Profile.objects.get_or_create(user=user)
        profile.group = self.cleaned_data['group']
        profile.phone = self.cleaned_data['phone']
        if commit:
            profile.save()
        return user
    
class UserCreationAdminForm(UserCreationForm):
    first_name = forms.CharField(label="Nombre", required=True)
    last_name  = forms.CharField(label="Apellido", required=True)
    email      = forms.EmailField(label="Correo electrónico", required=True)
    phone      = forms.CharField(label="Teléfono", required=False)
    group      = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        label="Rol / Perfil",
        required=True
    )

    class Meta(UserCreationForm.Meta):
        model  = User
        fields = ("username", "first_name", "last_name", "email",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Asignar clases bootstrap a todos los inputs/selects
        text_like = ["username", "first_name", "last_name", "email", "phone"]
        for name in text_like:
            if name in self.fields:
                self.fields[name].widget.attrs.update({"class": "form-control"})

        if "group" in self.fields:
            self.fields["group"].widget.attrs.update({"class": "form-select"})

        # Passwords con estilo
        if "password1" in self.fields:
            self.fields["password1"].widget.attrs.update({"class": "form-control"})
        if "password2" in self.fields:
            self.fields["password2"].widget.attrs.update({"class": "form-control"})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name  = self.cleaned_data["last_name"]
        user.email      = self.cleaned_data["email"]
        if commit:
            user.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.phone = self.cleaned_data.get("phone")
            profile.group = self.cleaned_data["group"]
            profile.save()
        return user

# --- Formulario para Crear/Editar Cuadrilla ---
class CuadrillaForm(forms.ModelForm):
    # Definir explícitamente los campos ForeignKey para filtrar
    departamento = forms.ModelChoiceField(
        queryset=Departamento.objects.filter(state='Activo'), # Solo Departamentos activos
        label="Departamento al que Pertenece",
        empty_label="Seleccione un departamento",
        widget=forms.Select(attrs={'class': 'form-select'}) # Estilo opcional
    )
    
    jefe = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True, profile__group__name='Cuadrilla'), # Solo Users activos con rol 'Cuadrilla'
        label="Jefe de Cuadrilla",
        empty_label="Seleccione un jefe ",
        widget=forms.Select(attrs={'class': 'form-select'}) # Estilo opcional
    )

    class Meta:
        model = Cuadrilla
        # Campos que se mostrarán en el formulario
        fields = ['nombre_cuadrilla', 'departamento', 'jefe'] 
        widgets = { # Opcional: para estilos
            'nombre_cuadrilla': forms.TextInput(attrs={'class': 'form-control'}),
            # Los widgets para departamento y jefe ya se definieron arriba
        }