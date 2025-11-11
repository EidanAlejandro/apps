from django.shortcuts import render
from django.conf import settings #importa el archivo settings
from django.contrib import messages #habilita la mesajería entre vistas
from django.contrib.auth.decorators import login_required #habilita el decorador que se niega el acceso a una función si no se esta logeado
from django.contrib.auth.models import Group, User # importa los models de usuarios y grupos
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator #permite la paqinación
from django.db.models import Avg, Count, Q #agrega funcionalidades de agregación a nuestros QuerySets
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseNotFound, HttpResponseRedirect) #Salidas alternativas al flujo de la aplicación se explicará mas adelante
from django.shortcuts import redirect, render #permite renderizar vistas basadas en funciones o redireccionar a otras funciones
from django.template import RequestContext # contexto del sistema
from django.views.decorators.csrf import csrf_exempt #decorador que nos permitira realizar conexiones csrf

from registration.models import Profile #importa el modelo profile, el que usaremos para los perfiles de usuarios
from requests.models import Solicitud

# Create your views here.
def home(request):
    return redirect('login')

@login_required
def pre_check_profile(request):
    #por ahora solo esta creada pero aún no la implementaremos
    pass

@login_required
def check_profile(request):  
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()    
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error con su usuario, por favor contactese con los administradores')              
        return redirect('login')
    if profile.group_id == 1:        
        return redirect('main_admin')
    else:
        return redirect('logout')

"""
#funcion temporal
@login_required
def main_admin(request):  
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()    
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error con su usuario, por favor contactese con los administradores')              
        return redirect('login')
    if profile.group_id == 1:        
        template_name = 'core/main_admin.html'
        return render(request,template_name)
    else:
        return redirect('logout')
"""

@login_required
def main_admin(request):  
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()    
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error con su usuario, por favor contactese con los administradores')              
        return redirect('login')

    if profile.group_id == 1: 
        # ===== CONTADORES DEL DASHBOARD =====
        total_usuarios = User.objects.count()

        incidencias_creadas = Solicitud.objects.filter(
            id_estado__nombre_estado__in=['Abierta', 'Creada']
        ).count()

        incidencias_derivadas = Solicitud.objects.filter(
            id_estado__nombre_estado='Derivada'
        ).count()

        incidencias_rechazadas = Solicitud.objects.filter(
            id_estado__nombre_estado='Rechazada'
        ).count()

        incidencias_finalizadas = Solicitud.objects.filter(
            id_estado__nombre_estado__in=['Finalizada', 'Resuelta', 'Validada']
        ).count()

        # Últimas incidencias creadas (máximo 5)
        incidencias_recientes = Solicitud.objects.order_by('-created')[:5]

        context = {
            'total_usuarios': total_usuarios,
            'incidencias_creadas': incidencias_creadas,
            'incidencias_derivadas': incidencias_derivadas,
            'incidencias_rechazadas': incidencias_rechazadas,
            'incidencias_finalizadas': incidencias_finalizadas,
            'incidencias_recientes': incidencias_recientes,
        }

        template_name = 'core/main_admin.html'
        return render(request, template_name, context)

    else:
        return redirect('logout')
