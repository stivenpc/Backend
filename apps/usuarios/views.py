from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import FormularioLogin, FormularioPerfil
from apps.auditoria.utils import registrar_log

def login_view(request):
    if request.user.is_authenticated:
        return redirect('operaciones:dashboard')

    if request.method == 'POST':
        form = FormularioLogin(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Bienvenido/a al Sistema de Fundición, {user.get_full_name() or user.username} ({user.perfil.get_rol_display()}).")
            
            # Redirección segura
            next_url = request.POST.get('next') or request.GET.get('next') or 'operaciones:dashboard'
            return redirect(next_url)
        else:
            messages.error(request, "Credenciales inválidas. Por favor verifique su usuario y contraseña.")
    else:
        form = FormularioLogin(request)

    return render(request, 'usuarios/login.html', {'form': form})

def logout_view(request):
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        messages.info(request, f"Sesión cerrada correctamente. Hasta pronto, {username}.")
    return redirect('usuarios:login')

@login_required
def perfil_view(request):
    perfil = request.user.perfil
    if request.method == 'POST':
        form = FormularioPerfil(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            registrar_log(
                accion='UPDATE',
                tabla_afectada='usuarios_perfilusuario',
                registro_id=perfil.id,
                detalles=f"Actualización de datos personales del perfil del usuario {request.user.username}",
                usuario=request.user
            )
            messages.success(request, "Perfil actualizado con éxito.")
            return redirect('usuarios:perfil')
    else:
        form = FormularioPerfil(instance=perfil)

    return render(request, 'usuarios/perfil.html', {'form': form, 'perfil': perfil})
