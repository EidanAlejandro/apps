# requests/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
# Importar User y Group de Django si necesitas verificar roles específicos aquí
from django.contrib.auth.models import User, Group 
from .models import Solicitud, Respuesta, Pregunta, EstadoSolicitud 
from .forms import SolicitudForm, RespuestaForm, MultimediaForm
from registration.models import Profile
from surveys.models import Encuesta, Pregunta # Corregido import Pregunta
# Quitar imports de Territorial y JefeCuadrilla si ya no existen esos modelos
# from users.models import Territorial, JefeCuadrilla 
from django.contrib import messages

@login_required
def main_requests(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist: return redirect('logout')

    # Podrías filtrar solicitudes según el rol del usuario (profile.group_id)
    # Ejemplo: Si es Territorial (ID 4), mostrar solo las suyas
    if profile.group_id == 4:
         solicitud_listado = Solicitud.objects.filter(state='Activo', id_territorial=request.user).order_by('-created')
    # Ejemplo: Si es Cuadrilla (ID 5), mostrar solo las asignadas a él
    elif profile.group_id == 5:
         solicitud_listado = Solicitud.objects.filter(state='Activo', id_cuadrilla=request.user).order_by('-created')
    # Si es Admin (ID 1) u otro rol, muestra todas
    else:
         solicitud_listado = Solicitud.objects.filter(state='Activo').order_by('-created')
    
    template_name = 'requests/main_requests.html'
    return render(request, template_name, {'solicitud_listado': solicitud_listado})

@login_required
def solicitud_crear(request):
    try:
        profile = Profile.objects.get(user=request.user)
        # Permitir crear a Admin (1) y Territorial (4)
        if profile.group_id not in [1, 4]: 
             messages.error(request, 'No tienes permiso para crear solicitudes.')
             return redirect('main_admin')
    except Profile.DoesNotExist: return redirect('logout')

    if request.method == 'POST':
        # Pasar request.user a la data si necesitas auto-asignar territorial
        # post_data = request.POST.copy()
        # if profile.group_id == 4: # Si es territorial quien crea
        #     post_data['id_territorial'] = request.user.id 
        # form = SolicitudForm(post_data)
        
        form = SolicitudForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            
            # Asignar estado inicial 'Creada' si no se seleccionó
            if not form.cleaned_data.get('id_estado'):
                try:
                    estado_inicial = EstadoSolicitud.objects.get(nombre_estado='Creada')
                    solicitud.id_estado = estado_inicial
                except EstadoSolicitud.DoesNotExist:
                     messages.warning(request, "Estado 'Creada' no encontrado.")
            
            # Si el usuario es Territorial, asignarlo automáticamente
            if profile.group_id == 4:
                 solicitud.id_territorial = request.user

            solicitud.save()
            form.save_m2m() 
            messages.success(request, 'Solicitud creada con éxito.')
            return redirect('main_requests')
        else:
             messages.error(request, 'Error en el formulario. Revisa los campos.')
    else:
        form = SolicitudForm()
        # Pre-seleccionar territorial si es él quien crea
        if profile.group_id == 4:
             form.fields['id_territorial'].initial = request.user
             # Opcional: Hacer el campo readonly si es territorial
             # form.fields['id_territorial'].widget.attrs['disabled'] = True 

    template_name = 'requests/solicitud_form.html'
    return render(request, template_name, {'form': form, 'titulo': 'Crear Solicitud'})

@login_required
def solicitud_ver(request, solicitud_id):
    solicitud = get_object_or_404(Solicitud, pk=solicitud_id)
    
    # Lógica de permisos: ¿Quién puede ver esta solicitud? (ej. Admin, el Territorial, la Cuadrilla asignada)
    
    preguntas = Pregunta.objects.filter(id_encuesta=solicitud.id_encuesta, state='Activo') # Filtrar activas
    respuestas_list = Respuesta.objects.filter(id_solicitud=solicitud).order_by('created')
    
    
    forms_respuestas = {}
    for pregunta in preguntas:
        forms_respuestas[pregunta.id_pregunta] = RespuestaForm() 
            
    # Formulario para multimedia general (si decides mantenerlo)
    multimedia_form = MultimediaForm()
            
    template_name = 'requests/solicitud_ver.html'
    return render(request, template_name, {
        'solicitud': solicitud,
        'preguntas': preguntas,
        'respuestas_list': respuestas_list, # Pasamos la lista
        'forms_respuestas': forms_respuestas, # Pasamos los forms vacíos
        'MultimediaForm': multimedia_form 
    })
    

@login_required
def solicitud_editar(request, solicitud_id):
    solicitud = get_object_or_404(Solicitud, pk=solicitud_id)
    # Lógica de permisos para editar (ej. Admin, Depto a cargo?)
    try:
        profile = Profile.objects.get(user=request.user)
        # Ejemplo: Solo Admin (1) puede editar todo por ahora
        if profile.group_id != 1: 
             messages.error(request, 'No tienes permiso para editar.')
             return redirect('main_requests')
    except Profile.DoesNotExist: return redirect('logout')

    if request.method == 'POST':
        form = SolicitudForm(request.POST, instance=solicitud)
        if form.is_valid():
            form.save()
            messages.success(request, 'Solicitud actualizada con éxito.')
            return redirect('main_requests')
    else:
        form = SolicitudForm(instance=solicitud)

    template_name = 'requests/solicitud_form.html'
    return render(request, template_name, {'form': form, 'titulo': 'Editar Solicitud', 'solicitud': solicitud}) # Pasar solicitud por si la necesitas en el template

# --- NUEVA VISTA SOLICITUD BLOQUEAR ---
@login_required
def solicitud_bloquear(request, solicitud_id):
    """ Cambia el estado de una Solicitud a 'Bloqueado'. """
    try:
        profile = Profile.objects.get(user=request.user)
        # Definir qué roles pueden bloquear (ej. Admin/SECPLA)
        if profile.group_id != 1: 
             messages.error(request, 'No tienes permiso para bloquear solicitudes.')
             return redirect('main_requests') 
    except Profile.DoesNotExist: return redirect('logout')

    solicitud_obj = get_object_or_404(Solicitud, pk=solicitud_id)
    solicitud_obj.state = 'Bloqueado'
    solicitud_obj.save()
    messages.info(request, f'Solicitud #{solicitud_obj.id_solicitud} bloqueada.')
    # Redirigir a la lista principal (donde ya no aparecerá)
    return redirect('main_requests') 

# --- NUEVA VISTA SOLICITUD LISTA BLOQUEADAS ---
@login_required
def solicitud_list_bloqueadas(request):
    """ Muestra la lista de Solicitudes bloqueadas. """
    try:
        profile = Profile.objects.get(user=request.user)
        # Definir qué roles pueden ver bloqueadas (ej. Admin/SECPLA)
        if profile.group_id != 1: 
             messages.error(request, 'No tienes permiso para ver solicitudes bloqueadas.')
             return redirect('main_admin')
    except Profile.DoesNotExist: return redirect('logout')

    solicitudes_bloqueadas = Solicitud.objects.filter(state='Bloqueado').order_by('-created')
    return render(request, 'requests/solicitud_list_bloqueadas.html', {'solicitudes_bloqueadas': solicitudes_bloqueadas})

# --- NUEVA VISTA SOLICITUD DESBLOQUEAR ---
@login_required
def solicitud_desbloquear(request, solicitud_id):
    """ Cambia el estado de una Solicitud a 'Activo'. """
    try:
        profile = Profile.objects.get(user=request.user)
        # Definir qué roles pueden desbloquear (ej. Admin/SECPLA)
        if profile.group_id != 1: 
             messages.error(request, 'No tienes permiso para desbloquear solicitudes.')
             return redirect('main_requests')
    except Profile.DoesNotExist: return redirect('logout')

    solicitud_obj = get_object_or_404(Solicitud, pk=solicitud_id)
    solicitud_obj.state = 'Activo'
    # Considera añadir validación clean() aquí si es necesario antes de activar
    solicitud_obj.save()
    messages.success(request, f'Solicitud #{solicitud_obj.id_solicitud} desbloqueada.')
    # Vuelve a la lista de bloqueadas para ver el cambio
    return redirect('solicitud_list_bloqueadas')

@login_required
def solicitud_eliminar(request, solicitud_id):
    solicitud = get_object_or_404(Solicitud, pk=solicitud_id)
    # Lógica de permisos para eliminar (ej. Solo Admin?)
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.group_id != 1: 
             messages.error(request, 'No tienes permiso para eliminar.')
             return redirect('main_requests')
    except Profile.DoesNotExist: return redirect('logout')

    titulo_solicitud = solicitud.titulo    
    solicitud.delete()
    messages.success(request, f'Solicitud "{titulo_solicitud}" eliminada.')
    return redirect('main_requests')

@login_required
def respuesta_guardar(request, solicitud_id, pregunta_id):
    solicitud = get_object_or_404(Solicitud, pk=solicitud_id)
    pregunta = get_object_or_404(Pregunta, pk=pregunta_id)
    # Lógica de permisos: ¿Quién puede responder? (ej. Cuadrilla asignada?)
    
    if request.method == 'POST':
        
        
        # Pasar la instancia existente si la hay (para actualizar en lugar de crear)
        form = RespuestaForm(request.POST) 
        
        if form.is_valid():
            respuesta = form.save(commit=False)
            respuesta.id_solicitud = solicitud
            respuesta.id_pregunta = pregunta
            respuesta.save() # Guarda una NUEVA respuesta cada vez
            messages.success(request, f'Nueva respuesta a "{pregunta.texto_pregunta}" guardada.')
            return redirect('solicitud_ver', solicitud_id=solicitud_id)
        else:
            error_msg = form.errors.as_text()
            messages.error(request, f'Error al guardar respuesta: {error_msg}')
            # Considera pasar el form con errores de vuelta si quieres mostrarlo
            return redirect('solicitud_ver', solicitud_id=solicitud_id)
    else:
        return redirect('solicitud_ver', solicitud_id=solicitud_id)

@login_required
def multimedia_subir(request, respuesta_id):
    """ 
    Gestiona la subida de archivos multimedia para una RESPUESTA específica.
    Recibe el ID de la Respuesta desde la URL.
    """
    # Obtener la respuesta a la que se adjuntará el archivo
    respuesta = get_object_or_404(Respuesta, pk=respuesta_id)
    # Obtener la solicitud asociada para poder redirigir de vuelta
    solicitud_id = respuesta.id_solicitud_id 
    
    # --- Lógica de Permisos ---
    # ¿Quién puede subir archivos a esta respuesta? 
    # Ejemplo: Solo el admin (SECPLA) o la cuadrilla asignada a la solicitud.
    try:
        profile = Profile.objects.get(user=request.user)
        # Verificar si es admin O si es la cuadrilla asignada a la solicitud de la respuesta
        es_admin = profile.group_id == 1
        es_cuadrilla_asignada = (respuesta.id_solicitud.id_cuadrilla == request.user)
        
        if not (es_admin or es_cuadrilla_asignada):
             messages.error(request, 'No tienes permiso para añadir multimedia a esta respuesta.')
             # Redirigir a la vista de la solicitud
             return redirect('solicitud_ver', solicitud_id=solicitud_id) 
             
    except Profile.DoesNotExist: 
        messages.error(request, 'Tu perfil no está configurado.')
        return redirect('logout')
    # --- Fin Lógica de Permisos ---

    if request.method == 'POST':
        # ¡IMPORTANTE! Pasar request.FILES al formulario para manejar la subida de archivos
        form = MultimediaForm(request.POST, request.FILES) 
        if form.is_valid():
            # Crear el objeto Multimedia pero no guardarlo aún en la BD
            multimedia = form.save(commit=False) 
            # Asociar el objeto Multimedia con la Respuesta correcta
            multimedia.id_respuesta = respuesta 
            # multimedia.id_solicitud = None # Asegurarse que no se asocie directamente a Solicitud
            
            # Ahora sí, guardar el objeto Multimedia en la base de datos
            multimedia.save() 
            
            messages.success(request, f'Archivo multimedia ({multimedia.get_tipo_display()}) añadido a la respuesta.')
            # Redirigir de vuelta a la vista de detalles de la SOLICITUD
            return redirect('solicitud_ver', solicitud_id=solicitud_id)
        else:
             # Si el formulario tiene errores (ej. archivo no válido, tipo faltante)
             error_msg = form.errors.as_text() # Obtener los errores como texto
             messages.error(request, f'Error al subir archivo: {error_msg}')
             # Redirigir de vuelta a la vista de detalles de la SOLICITUD para mostrar el error
             return redirect('solicitud_ver', solicitud_id=solicitud_id)
    else:
        # Si alguien intenta acceder a esta URL directamente con GET, 
        # no tiene sentido mostrar un formulario aquí. Lo redirigimos
        # a la vista de detalles de la solicitud donde SÍ está el formulario.
        return redirect('solicitud_ver', solicitud_id=solicitud_id)