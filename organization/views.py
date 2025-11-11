# organization/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# Importar User y Group de Django
from django.contrib.auth.models import User, Group
from .models import Direccion, Departamento
from .forms import DepartamentoForm
from registration.models import Profile # Para verificar el rol del usuario
from django.core.exceptions import ValidationError
from django.db.models import Count, Q 
from users.models import Cuadrilla  # Importar el modelo Cuadrilla para conteos
from django import forms
from users.models import Cuadrilla

# ===================================================================
# CRUD para DIRECCION
# ===================================================================

@login_required
def main_direccion(request):
    """ Muestra la lista de Direcciones activas y sus conteos (CON BÚSQUEDA). """
    try:
        profile = Profile.objects.get(user=request.user)
        # --- VERIFICACIÓN POR ID ---
        if profile.group_id != 1: # Solo Admin (ID=1)
            messages.error(request, 'No tienes permiso para ver esta página.')
            return redirect('logout') # O a 'main_admin'
    except Profile.DoesNotExist:
        messages.error(request, 'Error de perfil de usuario.')
        return redirect('login')


    query = request.GET.get('q', None) 
    

    direccion_listado_base = Direccion.objects.filter(state='Activo')

    if query:
        direccion_listado_base = direccion_listado_base.filter(
            Q(nombre_direccion__icontains=query) |
            Q(usuario__first_name__icontains=query) |
            Q(usuario__last_name__icontains=query)
        )




    direccion_listado = direccion_listado_base.annotate(
        num_departamentos=Count('departamento')
    ).order_by('nombre_direccion')


    total_departamentos_activos = Departamento.objects.filter(state='Activo').count()

    template_name = 'organization/main_direccion.html'
    

    context = {
        'direccion_listado': direccion_listado,
        'total_departamentos': total_departamentos_activos,
        'search_query': query, 
    }
    
    return render(request, template_name, context)

@login_required
def direccion_crear(request):
    """ Muestra el formulario para crear una nueva Dirección. """
    try:
        profile = Profile.objects.get(user=request.user)
        # --- VERIFICACIÓN POR ID ---
        if profile.group_id != 1: return redirect('logout')
    except Profile.DoesNotExist: return redirect('login')


    try:
        grupo_direccion = Group.objects.get(name='Direccion')
        usuarios_direccion = User.objects.filter(is_active=True, profile__group=grupo_direccion)
    except Group.DoesNotExist:
        usuarios_direccion = User.objects.none()
        messages.warning(request, "El grupo 'Direccion' no existe. No se pueden asignar encargados.")

    template_name = 'organization/direccion_crear.html'
    return render(request, template_name, {'usuarios': usuarios_direccion})

@login_required
def direccion_guardar(request):
    """ Guarda la nueva Dirección enviada por POST. """
    try:
        profile = Profile.objects.get(user=request.user)
        # --- VERIFICACIÓN POR ID ---
        if profile.group_id != 1: return redirect('logout')
    except Profile.DoesNotExist: return redirect('login')

    if request.method == 'POST':
        nombre = request.POST.get('nombre_direccion')
        usuario_id = request.POST.get('usuario')


        try:
            grupo_direccion = Group.objects.get(name='Direccion')
            usuarios_direccion = User.objects.filter(is_active=True, profile__group=grupo_direccion)
        except Group.DoesNotExist: usuarios_direccion = User.objects.none()

        if not nombre or not usuario_id:
            messages.error(request, 'Debes ingresar nombre y encargado.')
            return render(request, 'organization/direccion_crear.html', {'usuarios': usuarios_direccion})

        try:
            encargado = User.objects.get(pk=usuario_id)
            direccion_obj = Direccion(nombre_direccion=nombre, usuario=encargado)

            try:
                direccion_obj.full_clean() 
            except ValidationError as e:
                error_list = []
                for field, errors in e.message_dict.items():
                    error_list.append(f"{field}: {'; '.join(errors)}")
                messages.error(request, f"Error de validación: {'. '.join(error_list)}")
                return render(request, 'organization/direccion_crear.html', {'usuarios': usuarios_direccion})

            direccion_obj.save()
            messages.success(request, 'Dirección ingresada con éxito')
            return redirect('main_direccion')

        except User.DoesNotExist:
            messages.error(request, 'Usuario encargado no encontrado.')
            return render(request, 'organization/direccion_crear.html', {'usuarios': usuarios_direccion})
    else:
        return redirect('direccion_crear')

@login_required
def direccion_ver(request, direccion_id):
    """ Muestra los detalles de una Dirección específica y sus Departamentos. """
    try:
        profile = Profile.objects.get(user=request.user)
        # --- VERIFICACIÓN POR ID ---
        if profile.group_id != 1: return redirect('logout')
    except Profile.DoesNotExist: return redirect('login')

    direccion_data = get_object_or_404(Direccion, pk=direccion_id)
    

    departamentos_listado = Departamento.objects.filter(id_direccion=direccion_data).order_by('nombre_departamento')

    template_name = 'organization/direccion_ver.html'
    
    context = {
        'direccion_data': direccion_data,
        'departamentos_listado': departamentos_listado, 
    }
    return render(request, template_name, context)


@login_required
def direccion_editar(request, direccion_id):
    """ Muestra el formulario para editar una Dirección existente. """
    try:
        profile = Profile.objects.get(user=request.user)
        # --- VERIFICACIÓN POR ID ---
        if profile.group_id != 1: return redirect('logout')
    except Profile.DoesNotExist: return redirect('login')

    direccion_data = get_object_or_404(Direccion, pk=direccion_id)

    try:
        grupo_direccion = Group.objects.get(name='Direccion')
        usuarios_direccion = User.objects.filter(is_active=True, profile__group=grupo_direccion)
    except Group.DoesNotExist:
        usuarios_direccion = User.objects.none()
        messages.warning(request, "El grupo 'Direccion' no existe.")

    template_name = 'organization/direccion_editar.html'
    return render(request, template_name, {
        'direccion_data': direccion_data,
        'usuarios': usuarios_direccion
    })

@login_required
def direccion_actualizar(request):
    """ Actualiza una Dirección existente enviada por POST. """
    try:
        profile = Profile.objects.get(user=request.user)
        # --- VERIFICACIÓN POR ID ---
        if profile.group_id != 1: return redirect('logout')
    except Profile.DoesNotExist: return redirect('login')

    if request.method == 'POST':
        direccion_id = request.POST.get('id_direccion')
        nombre = request.POST.get('nombre_direccion')
        usuario_id = request.POST.get('usuario')

        direccion_obj = get_object_or_404(Direccion, pk=direccion_id) #
        try: 
            grupo_direccion = Group.objects.get(name='Direccion')
            usuarios_direccion = User.objects.filter(is_active=True, profile__group=grupo_direccion)
        except Group.DoesNotExist: usuarios_direccion = User.objects.none()


        if not nombre or not usuario_id or not direccion_id:
            messages.error(request, 'Faltan datos para actualizar.')
            return render(request, 'organization/direccion_editar.html', {
                'direccion_data': direccion_obj,
                'usuarios': usuarios_direccion
            })


        try:
            encargado = User.objects.get(pk=usuario_id)

            direccion_obj.nombre_direccion = nombre
            direccion_obj.usuario = encargado

            try:
                direccion_obj.full_clean() 
            except ValidationError as e:
                error_list = []
                for field, errors in e.message_dict.items():
                    error_list.append(f"{field}: {'; '.join(errors)}")
                messages.error(request, f"Error de validación: {'. '.join(error_list)}")
                return render(request, 'organization/direccion_editar.html', {
                    'direccion_data': direccion_obj,
                    'usuarios': usuarios_direccion
                })

            direccion_obj.save()
            messages.success(request, 'Dirección actualizada con éxito.')
            return redirect('main_direccion')

        except User.DoesNotExist:
            messages.error(request, 'Usuario encargado no encontrado.')
            return render(request, 'organization/direccion_editar.html', {
                'direccion_data': direccion_obj,
                'usuarios': usuarios_direccion
            })
    else:
        return redirect('main_direccion')

@login_required
def direccion_bloquea(request, direccion_id):
    """ Cambia el estado de una Dirección a 'Bloqueado'. """
    try:
        profile = Profile.objects.get(user=request.user)
        # --- VERIFICACIÓN POR ID ---
        if profile.group_id != 1: return redirect('logout')
    except Profile.DoesNotExist: return redirect('login')

    direccion_obj = get_object_or_404(Direccion, pk=direccion_id)
    direccion_obj.state = 'Bloqueado'
    direccion_obj.save()
    messages.info(request, f'Dirección "{direccion_obj.nombre_direccion}" bloqueada.')
    return redirect('main_direccion')

@login_required
def direccion_list_bloqueadas(request):
    """ Muestra la lista de Direcciones bloqueadas. """
    try:
        profile = Profile.objects.get(user=request.user)
        # --- VERIFICACIÓN POR ID ---
        if profile.group_id != 1:
            messages.error(request, 'No tienes permiso.')
            return redirect('main_admin')
    except Profile.DoesNotExist: return redirect('logout')

    direcciones_bloqueadas = Direccion.objects.filter(state='Bloqueado').order_by('nombre_direccion')
    return render(request, 'organization/direccion_list_bloqueadas.html', {'direcciones_bloqueadas': direcciones_bloqueadas})

@login_required
def direccion_desbloquear(request, direccion_id):
    """ Cambia el estado de una Dirección a 'Activo'. """
    try:
        profile = Profile.objects.get(user=request.user)
        # --- VERIFICACIÓN POR ID ---
        if profile.group_id != 1: return redirect('logout')
    except Profile.DoesNotExist: return redirect('login')

    direccion_obj = get_object_or_404(Direccion, pk=direccion_id)
    direccion_obj.state = 'Activo'

    direccion_obj.save()
    messages.success(request, f'Dirección "{direccion_obj.nombre_direccion}" desbloqueada.')
    return redirect('direccion_list_bloqueadas')

@login_required
def direccion_elimina(request, direccion_id):
    """ Elimina permanentemente una Dirección. """
    try:
        profile = Profile.objects.get(user=request.user)
        # --- VERIFICACIÓN POR ID ---
        if profile.group_id != 1: return redirect('logout')
    except Profile.DoesNotExist: return redirect('login')

    direccion_obj = get_object_or_404(Direccion, pk=direccion_id)
    nombre_direccion = direccion_obj.nombre_direccion
    direccion_obj.delete()
    messages.success(request, f'Dirección "{nombre_direccion}" eliminada permanentemente.')
    return redirect('main_direccion')


# ===================================================================
# CRUD para DEPARTAMENTO (Método con ModelForm)
# ===================================================================

@login_required
def main_departamento(request):
    """ Muestra la lista de Departamentos activos (CON BÚSQUEDA Y CONTEOS). """
    try:
        profile = Profile.objects.get(user=request.user)
        # --- VERIFICACIÓN POR ID ---
        if profile.group_id != 1: # Solo Admin (ID=1)
            messages.error(request, 'No tienes permiso para ver esta página.')
            return redirect('logout')
    except Profile.DoesNotExist:
        messages.error(request, 'Error de perfil de usuario.')
        return redirect('login')

    query = request.GET.get('q', None)
    
    departamento_listado_base = Departamento.objects.filter(state='Activo')

    if query:
        departamento_listado_base = departamento_listado_base.filter(
            Q(nombre_departamento__icontains=query) |
            Q(usuario__first_name__icontains=query) |
            Q(usuario__last_name__icontains=query) |
            Q(id_direccion__nombre_direccion__icontains=query) # Busca por nombre de dirección
        )

    # --- ¡CAMBIO 2: LÓGICA DE CONTEO REAL! ---
    
    # 1. Anotación para la lista (cuántas cuadrillas por depto)
    departamento_listado = departamento_listado_base.annotate(
        # Usamos 'cuadrilla_set' (el related_name por defecto)
        num_cuadrillas=Count('cuadrilla') 
    ).order_by('nombre_departamento')

    # 2. Conteo para la tarjeta de resumen (cuántas cuadrillas activas en total)
    total_cuadrillas_activas = Cuadrilla.objects.filter(state='Activo').count()
    
    # --- FIN DE LOS CAMBIOS ---

    template_name = 'organization/main_departamento.html'
    
    context = {
        'departamento_listado': departamento_listado,
        'total_cuadrillas': total_cuadrillas_activas, # Lo pasamos al template
        'search_query': query, 
    }
    return render(request, template_name, context)

@login_required
def departamento_crear(request):
    """ Muestra y procesa el formulario para crear un Departamento. """
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.group_id != 1: return redirect('logout')
    except Profile.DoesNotExist: return redirect('login')

    if request.method == 'POST':
        form = DepartamentoForm(request.POST)
    else:
        form = DepartamentoForm()

    # --- AÑADIR ESTE BLOQUE DE ESTILOS ---
    # (Aplica estilos en GET y en POST inválido)
    try:
        # Añadimos 'form-control' o 'form-select' a cada campo
        form.fields['nombre_departamento'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nombre del departamento'})
        form.fields['usuario'].widget.attrs.update({'class': 'form-select'})
        form.fields['id_direccion'].widget.attrs.update({'class': 'form-select'})
    except KeyError:
        pass # Ignora si algún campo no existe en el form
    # --- FIN DEL BLOQUE ---

    if request.method == 'POST':
        if form.is_valid(): 
            form.save()
            messages.success(request, 'Departamento creado con éxito')
            return redirect('main_departamento')
        else:
            messages.error(request, 'Error en el formulario. Revisa los campos.')
    
    # Hemos movido la lógica de POST/GET arriba para que los estilos se apliquen siempre
    template_name = 'organization/departamento_crear.html'
    return render(request, template_name, {'form': form})

@login_required
def departamento_ver(request, departamento_id):
    """ Muestra los detalles de un Departamento específico y sus cuadrillas. """
    try:
        profile = Profile.objects.get(user=request.user)
        # --- VERIFICACIÓN POR ID ---
        if profile.group_id != 1: return redirect('logout')
    except Profile.DoesNotExist: return redirect('login')

    departamento_data = get_object_or_404(Departamento, pk=departamento_id)
    
    try:
        cuadrillas_listado = Cuadrilla.objects.filter(departamento=departamento_data)
    except Exception:
        # Si falla (ej. el FK tiene otro nombre), envía una lista vacía
        cuadrillas_listado = [] 
        messages.error(request, 'No se pudieron cargar las cuadrillas. Verifica la configuración del modelo.')


    template_name = 'organization/departamento_ver.html'
    context = {
        'departamento_data': departamento_data,
        'cuadrillas_listado': cuadrillas_listado,
    }
    return render(request, template_name, context)


@login_required
def departamento_editar(request, departamento_id):
    """ Myectra y procesa el formulario para editar un Departamento. """
    try:
        profile = Profile.objects.get(user=request.user)
        # --- VERIFICACIÓN POR ID ---
        if profile.group_id != 1: return redirect('logout')
    except Profile.DoesNotExist: return redirect('login')

    departamento = get_object_or_404(Departamento, pk=departamento_id)
    if request.method == 'POST':
        form = DepartamentoForm(request.POST, instance=departamento)
        if form.is_valid(): 
            form.save()
            messages.success(request, 'Departamento actualizado con éxito')
            return redirect('main_departamento')
        else:
            messages.error(request, 'Error en el formulario. Revisa los campos.')
    else:
        form = DepartamentoForm(instance=departamento)

    template_name = 'organization/departamento_editar.html'
    return render(request, template_name, {'form': form, 'departamento': departamento})

@login_required
def departamento_bloquea(request, departamento_id):
    """ Cambia el estado de un Departamento a 'Bloqueado'. """
    try:
        profile = Profile.objects.get(user=request.user)
        # --- VERIFICACIÓN POR ID ---
        if profile.group_id != 1: return redirect('logout')
    except Profile.DoesNotExist: return redirect('login')

    departamento_obj = get_object_or_404(Departamento, pk=departamento_id)
    departamento_obj.state = 'Bloqueado'
    departamento_obj.save()
    messages.info(request, f'Departamento "{departamento_obj.nombre_departamento}" bloqueado.')
    return redirect('main_departamento')

@login_required
def departamento_list_bloqueados(request):
    """ Muestra la lista de Departamentos bloqueados. """
    try:
        profile = Profile.objects.get(user=request.user)
        # --- VERIFICACIÓN POR ID ---
        if profile.group_id != 1:
            messages.error(request, 'No tienes permiso.')
            return redirect('main_admin')
    except Profile.DoesNotExist: return redirect('logout')

    departamentos_bloqueados = Departamento.objects.filter(state='Bloqueado').order_by('nombre_departamento')
    return render(request, 'organization/departamento_list_bloqueados.html', {'departamentos_bloqueados': departamentos_bloqueados})

@login_required
def departamento_desbloquear(request, departamento_id):
    """ Cambia el estado de un Departamento a 'Activo'. """
    try:
        profile = Profile.objects.get(user=request.user)
        # --- VERIFICACIÓN POR ID ---
        if profile.group_id != 1: return redirect('logout')
    except Profile.DoesNotExist: return redirect('login')

    departamento_obj = get_object_or_404(Departamento, pk=departamento_id)
    departamento_obj.state = 'Activo'

    try:
           departamento_obj.full_clean()
    except ValidationError as e:
        error_list = []
        for field, errors in e.message_dict.items():
            error_list.append(f"{field}: {'; '.join(errors)}")
        messages.error(request, f"No se puede desbloquear. Error: {'. '.join(error_list)}")
        return redirect('departamento_list_bloqueados')

    departamento_obj.save()
    messages.success(request, f'Departamento "{departamento_obj.nombre_departamento}" desbloqueado.')
    return redirect('departamento_list_bloqueados')

@login_required
def departamento_elimina(request, departamento_id):
    """ Elimina permanentemente un Departamento. """
    try:
        profile = Profile.objects.get(user=request.user)
        # --- VERIFICACIÓN POR ID ---
        if profile.group_id != 1: return redirect('logout')
    except Profile.DoesNotExist: return redirect('login')

    departamento_obj = get_object_or_404(Departamento, pk=departamento_id)
    nombre_departamento = departamento_obj.nombre_departamento
    departamento_obj.delete()
    messages.success(request, f'Departamento "{nombre_departamento}" eliminado permanentemente.')
    return redirect('main_departamento')

