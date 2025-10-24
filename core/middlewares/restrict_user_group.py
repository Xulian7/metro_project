from django.shortcuts import redirect
from django.urls import reverse

class RestrictUserGroupMiddleware:
    """
    Restringe el acceso a la app 'almacen' para los usuarios del grupo 'User'.
    Si intentan acceder, se los redirige al home.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        user = request.user

        # Ignorar rutas públicas, login o admin
        if any(path.startswith(p) for p in [
            reverse('admin:index'),
            '/login',
            '/logout',
            '/',
        ]):
            return self.get_response(request)

        # Si el usuario no está autenticado → al login
        if not user.is_authenticated:
            return redirect('/login')

        # 🚫 Si pertenece al grupo "User" y entra a la app "almacen"
        if path.startswith('/almacen') and user.groups.filter(name='User').exists():
            return redirect('/')  # redirige al home

        return self.get_response(request)
