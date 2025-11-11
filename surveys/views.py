from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import TipoEncuesta, Encuesta, Pregunta
from organization.models import Departamento
from registration.models import Profile

# ===================================================================
# CRUD para TIPO ENCUESTA
# ===================================================================

@login_required
def main_tipo_encuesta(request):
    """Vista principal de tipos de encuesta"""
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.error(request, 'Error de perfil de usuario')
        return redirect('login')
    
    if profile.group_id == 1:  # Solo administradores
        tipo_encuesta_listado = TipoEncuesta.objects.filter(state='Activo').order_by('nombre_tipo')
        template_name = 'surveys/main_tipo_encuesta.html'
        return render(request, template_name, {'tipo_encuesta_listado': tipo_encuesta_listado})
    else:
        return redirect('logout')

@login_required
def tipo_encuesta_crear(request):
    """Vista para crear tipo de encuesta"""
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        return redirect('login')
    
    if profile.group_id != 1:
        return redirect('logout')
    
    if request.method == 'POST':
        nombre_tipo = request.POST.get('nombre_tipo')
        
        if not nombre_tipo:
            messages.error(request, 'El nombre del tipo es obligatorio')
            return redirect('tipo_encuesta_crear')
        
        tipo_encuesta = TipoEncuesta(nombre_tipo=nombre_tipo)
        tipo_encuesta.save()
        messages.success(request, 'Tipo de encuesta creado exitosamente')
        return redirect('main_tipo_encuesta')
    
    template_name = 'surveys/tipo_encuesta_crear.html'
    return render(request, template_name)

@login_required
def tipo_encuesta_editar(request, tipo_encuesta_id):
    """Vista para editar tipo de encuesta"""
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        return redirect('login')
    
    if profile.group_id != 1:
        return redirect('logout')
    
    tipo_encuesta = get_object_or_404(TipoEncuesta, id_tipo_encuesta=tipo_encuesta_id)
    
    if request.method == 'POST':
        nombre_tipo = request.POST.get('nombre_tipo')
        
        if not nombre_tipo:
            messages.error(request, 'El nombre del tipo es obligatorio')
            return redirect('tipo_encuesta_editar', tipo_encuesta_id=tipo_encuesta_id)
        
        tipo_encuesta.nombre_tipo = nombre_tipo
        tipo_encuesta.save()
        messages.success(request, 'Tipo de encuesta actualizado exitosamente')
        return redirect('main_tipo_encuesta')
    
    template_name = 'surveys/tipo_encuesta_editar.html'
    return render(request, template_name, {'tipo_encuesta': tipo_encuesta})

@login_required
def tipo_encuesta_eliminar(request, tipo_encuesta_id):
    """Vista para eliminar tipo de encuesta"""
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        return redirect('login')
    
    if profile.group_id == 1:
        TipoEncuesta.objects.filter(id_tipo_encuesta=tipo_encuesta_id).delete()
        messages.success(request, 'Tipo de encuesta eliminado exitosamente')
    
    return redirect('main_tipo_encuesta')

# ===================================================================
# CRUD para ENCUESTA
# ===================================================================

@login_required
def main_encuesta(request):
    """Vista principal de encuestas"""
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.error(request, 'Error de perfil de usuario')
        return redirect('login')
    
    if profile.group_id == 1:
        encuesta_listado = Encuesta.objects.filter(state='Activo').order_by('titulo')
        template_name = 'surveys/main_encuesta.html'
        return render(request, template_name, {'encuesta_listado': encuesta_listado})
    else:
        return redirect('logout')

@login_required
def encuesta_crear(request):
    """Vista para crear encuesta"""
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        return redirect('login')
    
    if profile.group_id != 1:
        return redirect('logout')
    
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        id_departamento = request.POST.get('id_departamento')
        id_tipo_encuesta = request.POST.get('id_tipo_encuesta')
        
        if not all([titulo, id_departamento, id_tipo_encuesta]):
            messages.error(request, 'Todos los campos obligatorios deben ser llenados')
            return redirect('encuesta_crear')
        
        try:
            departamento = Departamento.objects.get(id_departamento=id_departamento)
            tipo_encuesta = TipoEncuesta.objects.get(id_tipo_encuesta=id_tipo_encuesta)
            
            encuesta = Encuesta(
                titulo=titulo,
                descripcion=descripcion,
                id_departamento=departamento,
                id_tipo_encuesta=tipo_encuesta
            )
            encuesta.save()
            messages.success(request, 'Encuesta creada exitosamente')
            return redirect('main_encuesta')
        except (Departamento.DoesNotExist, TipoEncuesta.DoesNotExist):
            messages.error(request, 'Departamento o tipo de encuesta no válido')
    
    # Obtener datos para los dropdowns
    departamentos = Departamento.objects.filter(state='Activo')
    tipos_encuesta = TipoEncuesta.objects.filter(state='Activo')
    
    template_name = 'surveys/encuesta_crear.html'
    return render(request, template_name, {
        'departamentos': departamentos,
        'tipos_encuesta': tipos_encuesta
    })

# --- NUEVA VISTA ENCUESTA VER ---
@login_required
def encuesta_ver(request, encuesta_id):
    """ Muestra los detalles de una Encuesta específica. """
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.group_id != 1: 
            messages.error(request, 'Acceso denegado.')
            return redirect('logout')
    except Profile.DoesNotExist: return redirect('login')

    encuesta_data = get_object_or_404(Encuesta, pk=encuesta_id)
    # Obtener las preguntas asociadas a esta encuesta
    preguntas_asociadas = Pregunta.objects.filter(id_encuesta=encuesta_data, state='Activo')
    
    template_name = 'surveys/encuesta_ver.html' # Necesitas crear este template
    return render(request, template_name, {
        'encuesta_data': encuesta_data,
        'preguntas_asociadas': preguntas_asociadas
        })


@login_required
def encuesta_editar(request, encuesta_id):
    """Vista para editar encuesta"""
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        return redirect('login')
    
    if profile.group_id != 1:
        return redirect('logout')
    
    encuesta = get_object_or_404(Encuesta, id_encuesta=encuesta_id)
    
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        id_departamento = request.POST.get('id_departamento')
        id_tipo_encuesta = request.POST.get('id_tipo_encuesta')
        
        if not all([titulo, id_departamento, id_tipo_encuesta]):
            messages.error(request, 'Todos los campos obligatorios deben ser llenados')
            return redirect('encuesta_editar', encuesta_id=encuesta_id)
        
        try:
            departamento = Departamento.objects.get(id_departamento=id_departamento)
            tipo_encuesta = TipoEncuesta.objects.get(id_tipo_encuesta=id_tipo_encuesta)
            
            encuesta.titulo = titulo
            encuesta.descripcion = descripcion
            encuesta.id_departamento = departamento
            encuesta.id_tipo_encuesta = tipo_encuesta
            encuesta.save()
            messages.success(request, 'Encuesta actualizada exitosamente')
            return redirect('encuesta_list_bloqueadas')
        except (Departamento.DoesNotExist, TipoEncuesta.DoesNotExist):
            messages.error(request, 'Departamento o tipo de encuesta no válido')
    
    departamentos = Departamento.objects.filter(state='Activo')
    tipos_encuesta = TipoEncuesta.objects.filter(state='Activo')
    
    template_name = 'surveys/encuesta_editar.html'
    return render(request, template_name, {
        'encuesta': encuesta,
        'departamentos': departamentos,
        'tipos_encuesta': tipos_encuesta
    })


# --- NUEVA VISTA ENCUESTA BLOQUEAR ---
@login_required
def encuesta_bloquear(request, encuesta_id):
    """ Cambia el estado de una Encuesta a 'Bloqueado'. """
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.group_id != 1: return redirect('logout')
    except Profile.DoesNotExist: return redirect('login')
        
    encuesta_obj = get_object_or_404(Encuesta, pk=encuesta_id)
    encuesta_obj.state = 'Bloqueado'
    encuesta_obj.save()
    messages.info(request, f'Encuesta "{encuesta_obj.titulo}" bloqueada. Ahora puede ser editada.')
    return redirect('encuesta_list_bloqueadas') 

# --- NUEVA VISTA ENCUESTA DESBLOQUEAR ---
@login_required
def encuesta_desbloquear(request, encuesta_id):
    """ Cambia el estado de una Encuesta a 'Activo'. """
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.group_id != 1: return redirect('logout')
    except Profile.DoesNotExist: return redirect('login')

    encuesta_obj = get_object_or_404(Encuesta, pk=encuesta_id)
    encuesta_obj.state = 'Activo'
    # Considera añadir validación clean() si es necesario antes de activar
    encuesta_obj.save()
    messages.success(request, f'Encuesta "{encuesta_obj.titulo}" desbloqueada/activada.')
    # Decide si redirigir a la lista principal o a la de bloqueadas
    return redirect('main_encuesta') 

# --- NUEVA VISTA ENCUESTA LISTA BLOQUEADAS ---
@login_required
def encuesta_list_bloqueadas(request):
    """ Muestra la lista de Encuestas bloqueadas. """
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.group_id != 1: 
            messages.error(request, 'No tienes permiso.')
            return redirect('main_admin')
    except Profile.DoesNotExist: return redirect('logout')

    encuestas_bloqueadas = Encuesta.objects.filter(state='Bloqueado').order_by('titulo')
    return render(request, 'surveys/encuesta_list_bloqueadas.html', {'encuestas_bloqueadas': encuestas_bloqueadas}) # Necesitas crear este template




@login_required
def encuesta_eliminar(request, encuesta_id):
    """Vista para eliminar encuesta"""
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        return redirect('login')
    
    if profile.group_id == 1:
        Encuesta.objects.filter(id_encuesta=encuesta_id).delete()
        messages.success(request, 'Encuesta eliminada exitosamente')
    
    return redirect('main_encuesta')

# ===================================================================
# CRUD para PREGUNTA
# ===================================================================

@login_required
def main_pregunta(request, encuesta_id):
    """Vista principal de preguntas de una encuesta"""
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.error(request, 'Error de perfil de usuario')
        return redirect('login')
    
    if profile.group_id == 1:
        encuesta = get_object_or_404(Encuesta, id_encuesta=encuesta_id)
        pregunta_listado = Pregunta.objects.filter(id_encuesta=encuesta_id, state='Activo').order_by('created')
        template_name = 'surveys/main_pregunta.html'
        return render(request, template_name, {
            'pregunta_listado': pregunta_listado,
            'encuesta': encuesta
        })
    else:
        return redirect('logout')

@login_required
def pregunta_crear(request, encuesta_id):
    """Vista para crear pregunta"""
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        return redirect('login')
    
    if profile.group_id != 1:
        return redirect('logout')
    
    encuesta = get_object_or_404(Encuesta, id_encuesta=encuesta_id)
    
    if request.method == 'POST':
        texto_pregunta = request.POST.get('texto_pregunta')
        
        if not texto_pregunta:
            messages.error(request, 'El texto de la pregunta es obligatorio')
            return redirect('pregunta_crear', encuesta_id=encuesta_id)
        
        pregunta = Pregunta(
            texto_pregunta=texto_pregunta,
            id_encuesta=encuesta
        )
        pregunta.save()
        messages.success(request, 'Pregunta creada exitosamente')
        return redirect('main_pregunta', encuesta_id=encuesta_id)
    
    template_name = 'surveys/pregunta_crear.html'
    return render(request, template_name, {'encuesta': encuesta})

@login_required
def pregunta_editar(request, pregunta_id):
    """Vista para editar pregunta"""
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        return redirect('login')
    
    if profile.group_id != 1:
        return redirect('logout')
    
    pregunta = get_object_or_404(Pregunta, id_pregunta=pregunta_id)
    
    if request.method == 'POST':
        texto_pregunta = request.POST.get('texto_pregunta')
        
        if not texto_pregunta:
            messages.error(request, 'El texto de la pregunta es obligatorio')
            return redirect('pregunta_editar', pregunta_id=pregunta_id)
        
        pregunta.texto_pregunta = texto_pregunta
        pregunta.save()
        messages.success(request, 'Pregunta actualizada exitosamente')
        return redirect('main_pregunta', encuesta_id=pregunta.id_encuesta.id_encuesta)
    
    template_name = 'surveys/pregunta_editar.html'
    return render(request, template_name, {'pregunta': pregunta})

@login_required
def pregunta_eliminar(request, pregunta_id):
    """Vista para eliminar pregunta"""
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        return redirect('login')
    
    if profile.group_id == 1:
        pregunta = get_object_or_404(Pregunta, id_pregunta=pregunta_id)
        encuesta_id = pregunta.id_encuesta.id_encuesta
        pregunta.delete()
        messages.success(request, 'Pregunta eliminada exitosamente')
        return redirect('main_pregunta', encuesta_id=encuesta_id)
    
    return redirect('main_encuesta')