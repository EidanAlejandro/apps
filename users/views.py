# users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from registration.models import Profile
# Importar los formularios de esta app
from .forms import UserProfileForm, CuadrillaForm, UserCreationAdminForm
from django.contrib import messages
# Importar modelo Cuadrilla
from .models import Cuadrilla 

from django.utils import timezone
from datetime import timedelta

from django import forms

# ===================================================================
# Vistas para Gestión de Usuarios (User de Django + Profile)
# ===================================================================

@login_required
def user_list(request):
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.group_id != 1: 
            messages.error(request, 'No tienes permiso para gestionar usuarios.')
            return redirect('main_admin') 
    except Profile.DoesNotExist:
        messages.error(request, 'Tu perfil no está configurado.')
        return redirect('logout')

    # --- INICIO DE CÁLCULOS PARA TARJETAS ---
    
    # 1. Lista de usuarios para la tabla (los activos)
    users_list = User.objects.filter(is_active=True).order_by('username')
    
    # 2. Cálculos para las tarjetas de resumen
    total_usuarios = User.objects.count()
    usuarios_activos = users_list.count() # Contamos solo los activos de la lista
    
    # Asumimos que el group_id=1 es para 'Administradores' y que contamos solo los activos
    total_administradores = Profile.objects.filter(group_id=1, user__is_active=True).count() 
    
    # Usuarios creados en los últimos 30 días
    un_mes_atras = timezone.now() - timedelta(days=30)
    nuevos_usuarios_mes = User.objects.filter(date_joined__gte=un_mes_atras).count()

    # --- FIN DE CÁLCULOS ---

    # 3. Definir el contexto que se envía a la plantilla
    context = {
        'users': users_list, # La lista para la tabla
        'total_usuarios': total_usuarios,
        'usuarios_activos': usuarios_activos,
        'total_administradores': total_administradores,
        'nuevos_usuarios_mes': nuevos_usuarios_mes,
    }
    
    return render(request, 'users/user_list.html', context) # <-- Pasar el nuevo context

@login_required
def user_crear(request):
    """ Permite al Admin (SECPLA) crear un nuevo usuario y asignarle grupo, teléfono, etc. """
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.group_id != 1:  # Solo SECPLA/Admin
            messages.error(request, "No tienes permiso para crear usuarios.")
            return redirect('main_admin')
    except Profile.DoesNotExist:
        messages.error(request, "Tu perfil no está configurado.")
        return redirect('logout')

    from .forms import UserCreationAdminForm
    if request.method == "POST":
        form = UserCreationAdminForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario creado correctamente.")
            return redirect('user_list')
        else:
            messages.error(request, "Error al crear el usuario. Revisa los campos.")
    else:
        form = UserCreationAdminForm()

    return render(request, 'users/user_create_form.html', {'form': form})

@login_required
def user_ver(request, user_id):
    try:
        admin_profile = Profile.objects.get(user=request.user)
        if admin_profile.group_id != 1: 
            messages.error(request, 'No tienes permiso.')
            return redirect('main_admin')
    except Profile.DoesNotExist: return redirect('logout')

    user_data = get_object_or_404(User, pk=user_id)
    try:
        # Usamos select_related para traer el grupo en la misma consulta
        profile_data = Profile.objects.select_related('group').get(user=user_data) 
    except Profile.DoesNotExist:
        profile_data = None
        messages.warning(request, f"El usuario {user_data.username} no tiene un perfil asociado.")

    template_name = 'users/user_ver.html' 
    return render(request, template_name, {'user_data': user_data, 'profile_data': profile_data})

@login_required
def user_edit(request, user_id):
    try:
        admin_profile = Profile.objects.get(user=request.user)
        if admin_profile.group_id != 1:
            messages.error(request, 'No tienes permiso para editar usuarios.')
            return redirect('main_admin')
    except Profile.DoesNotExist:
        messages.error(request, 'Tu perfil no está configurado.')
        return redirect('logout')

    user_to_edit = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        # Pasamos instance=user_to_edit para que el form sepa que está editando
        form = UserProfileForm(request.POST, instance=user_to_edit)

        # (Para aplicar estilos si el formulario es inválido y se vuelve a mostrar)
        try:
            form.fields['first_name'].widget.attrs.update({'class': 'form-control'})
            form.fields['last_name'].widget.attrs.update({'class': 'form-control'})
            form.fields['email'].widget.attrs.update({'class': 'form-control'})
            form.fields['phone'].widget.attrs.update({'class': 'form-control'})
            form.fields['group'].widget.attrs.update({'class': 'form-select'})
        except KeyError:
            # Si el formulario no tiene uno de estos campos, simplemente lo ignora.
            pass

        if form.is_valid():
            form.save() # El método save del form actualiza User y Profile
            messages.success(request, f'Usuario {user_to_edit.username} actualizado.')
            return redirect('user_list')
        else:
            messages.error(request, 'Error en el formulario. Revisa los campos.')
    else:
        # Pasamos instance=user_to_edit para que el form se cargue con los datos
        form = UserProfileForm(instance=user_to_edit) 

        # (Para aplicar estilos cuando se carga el formulario por primera vez)
        try:
            form.fields['first_name'].widget.attrs.update({'class': 'form-control'})
            form.fields['last_name'].widget.attrs.update({'class': 'form-control'})
            form.fields['email'].widget.attrs.update({'class': 'form-control'})
            form.fields['phone'].widget.attrs.update({'class': 'form-control'})
            form.fields['group'].widget.attrs.update({'class': 'form-select'})
        except KeyError:
            pass

    return render(request, 'users/user_edit_form.html', {'form': form, 'user_to_edit': user_to_edit})

@login_required
def user_bloquear(request, user_id):
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.group_id != 1: return redirect('main_admin') 
    except Profile.DoesNotExist: return redirect('logout')

    user_to_block = get_object_or_404(User, pk=user_id)
    if user_to_block == request.user:
        messages.error(request, 'No puedes bloquear tu propia cuenta.')
        return redirect('user_list')
        
    user_to_block.is_active = False 
    user_to_block.save()
    messages.success(request, f'Usuario {user_to_block.username} bloqueado.')
    return redirect('user_list')

@login_required
def user_list_bloqueados(request):
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.group_id != 1: 
            messages.error(request, 'No tienes permiso.')
            return redirect('main_admin')
    except Profile.DoesNotExist: return redirect('logout')

    users_bloqueados = User.objects.filter(is_active=False).order_by('username')
    return render(request, 'users/user_list_bloqueados.html', {'users_bloqueados': users_bloqueados})

@login_required
def user_desbloquear(request, user_id):
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.group_id != 1: return redirect('main_admin')
    except Profile.DoesNotExist: return redirect('logout')

    user_to_unblock = get_object_or_404(User, pk=user_id)
    user_to_unblock.is_active = True 
    user_to_unblock.save()
    messages.success(request, f'Usuario {user_to_unblock.username} desbloqueado.')
    return redirect('user_list_bloqueados')

@login_required
def user_delete(request, user_id):
    try:
        admin_profile = Profile.objects.get(user=request.user)
        if admin_profile.group_id != 1:
            messages.error(request, 'No tienes permiso para eliminar usuarios.')
            return redirect('main_admin')
    except Profile.DoesNotExist:
        messages.error(request, 'Tu perfil no está configurado.')
        return redirect('logout')

    user_to_delete = get_object_or_404(User, pk=user_id)
    if user_to_delete == request.user:
        messages.error(request, 'No puedes eliminar tu propia cuenta.')
        return redirect('user_list')

    username = user_to_delete.username
    user_to_delete.delete() # Esto borra el User y el Profile asociado (por CASCADE)
    messages.success(request, f'Usuario {username} eliminado.')
    return redirect('user_list')

# ===================================================================
# Vistas para Gestión de Cuadrillas
# ===================================================================

@login_required
def cuadrilla_list(request):
    """ Muestra la lista de Cuadrillas activas. """
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.group_id != 1: # Solo Admin/SECPLA
            messages.error(request, 'No tienes permiso para ver cuadrillas.')
            return redirect('main_admin') 
    except Profile.DoesNotExist: return redirect('logout')

    cuadrillas = Cuadrilla.objects.filter(state='Activo').order_by('nombre_cuadrilla')
    return render(request, 'users/cuadrilla_list.html', {'cuadrillas': cuadrillas})

@login_required
def cuadrilla_crear(request):
    """ Muestra y procesa el formulario para crear una Cuadrilla. """
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.group_id != 1: return redirect('main_admin')
    except Profile.DoesNotExist: return redirect('logout')
    
    if request.method == 'POST':
        form = CuadrillaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cuadrilla creada exitosamente.')
            return redirect('cuadrilla_list')
        else:
            messages.error(request, 'Error en el formulario. Revisa los campos.')
    else:
        form = CuadrillaForm() 
    
    return render(request, 'users/cuadrilla_form.html', {'form': form, 'titulo': 'Crear Nueva Cuadrilla'})

@login_required
def cuadrilla_ver(request, cuadrilla_id):
    """ Muestra los detalles de una Cuadrilla específica. """
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.group_id != 1: # Solo Admin/SECPLA
            messages.error(request, 'No tienes permiso.')
            return redirect('main_admin')
    except Profile.DoesNotExist: return redirect('logout')

    cuadrilla_data = get_object_or_404(Cuadrilla, pk=cuadrilla_id)
    template_name = 'users/cuadrilla_ver.html' 
    return render(request, template_name, {'cuadrilla_data': cuadrilla_data})

@login_required
def cuadrilla_editar(request, cuadrilla_id):
    """ Muestra y procesa el formulario para editar una Cuadrilla. """
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.group_id != 1: return redirect('main_admin')
    except Profile.DoesNotExist: return redirect('logout')
    
    cuadrilla = get_object_or_404(Cuadrilla, pk=cuadrilla_id)
    if request.method == 'POST':
        form = CuadrillaForm(request.POST, instance=cuadrilla)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cuadrilla actualizada exitosamente.')
            return redirect('cuadrilla_list')
        else:
            messages.error(request, 'Error en el formulario. Revisa los campos.')
    else:
        form = CuadrillaForm(instance=cuadrilla)
        
    return render(request, 'users/cuadrilla_form.html', {'form': form, 'titulo': 'Editar Cuadrilla', 'cuadrilla': cuadrilla})

@login_required
def cuadrilla_bloquear(request, cuadrilla_id):
    """ Cambia el estado de una Cuadrilla a 'Bloqueado'. """
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.group_id != 1: return redirect('main_admin') 
    except Profile.DoesNotExist: return redirect('logout')

    cuadrilla_obj = get_object_or_404(Cuadrilla, pk=cuadrilla_id)
    cuadrilla_obj.state = 'Bloqueado'
    cuadrilla_obj.save()
    messages.info(request, f'Cuadrilla "{cuadrilla_obj.nombre_cuadrilla}" bloqueada.')
    return redirect('cuadrilla_list') 

# --- NUEVA VISTA CUADRILLA BLOQUEADAS ---
@login_required
def cuadrilla_list_bloqueadas(request):
    """ Muestra la lista de Cuadrillas bloqueadas. """
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.group_id != 1: 
            messages.error(request, 'No tienes permiso.')
            return redirect('main_admin')
    except Profile.DoesNotExist: return redirect('logout')

    cuadrillas_bloqueadas = Cuadrilla.objects.filter(state='Bloqueado').order_by('nombre_cuadrilla')
    return render(request, 'users/cuadrilla_list_bloqueadas.html', {'cuadrillas_bloqueadas': cuadrillas_bloqueadas})

# --- NUEVA VISTA CUADRILLA DESBLOQUEAR ---
@login_required
def cuadrilla_desbloquear(request, cuadrilla_id):
    """ Cambia el estado de una Cuadrilla a 'Activo'. """
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.group_id != 1: return redirect('main_admin')
    except Profile.DoesNotExist: return redirect('logout')

    cuadrilla_obj = get_object_or_404(Cuadrilla, pk=cuadrilla_id)
    cuadrilla_obj.state = 'Activo'
    # Considera añadir validación clean() aquí si necesitas verificar algo antes de activar
    cuadrilla_obj.save()
    messages.success(request, f'Cuadrilla "{cuadrilla_obj.nombre_cuadrilla}" desbloqueada.')
    return redirect('cuadrilla_list_bloqueadas') # Vuelve a la lista de bloqueadas

@login_required
def cuadrilla_eliminar(request, cuadrilla_id):
    """ Elimina permanentemente una Cuadrilla. """
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.group_id != 1: 
            messages.error(request, 'No tienes permiso para eliminar.')
            return redirect('main_admin')
    except Profile.DoesNotExist: return redirect('logout')

    cuadrilla_obj = get_object_or_404(Cuadrilla, pk=cuadrilla_id)
    nombre_cuadrilla = cuadrilla_obj.nombre_cuadrilla 
    cuadrilla_obj.delete()
    messages.success(request, f'Cuadrilla "{nombre_cuadrilla}" eliminada permanentemente.')
    return redirect('cuadrilla_list')