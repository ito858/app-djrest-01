from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from .serializers import LoginSerializer
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.views import View
from apps.core.services.client_service import add_client
from django.contrib import messages


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            if user:
                login(request, user) # Redirect to dashboard
                return  redirect('dashboard')
#             Response({"message": "Logged in"}, status=status.HTTP_200_OK)
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def dashboard_view(request):
    group_name = request.user.groups.first().name if request.user.groups.exists() else "None"
    has_viewer_permission = request.user.has_perm('core.can_view_item')
    has_editor_permission = request.user.has_perm('core.can_edit_item')

    if request.method == 'POST' and has_editor_permission:
        nome_negozio = request.POST.get('nome_negozio')
        telefono = request.POST.get('telefono')
        if not nome_negozio or not telefono:
            messages.error(request, "Nome Negozio and Telefono are required.")
        else:
            data = {
                'nome_negozio': nome_negozio,
                'telefono': telefono,
                'tipo_negozio': request.POST.get('tipo_negozio', ''),
                'indirizzo': request.POST.get('indirizzo', ''),
                'citta': request.POST.get('citta', ''),
                'provincia': request.POST.get('provincia', ''),
                'cap': request.POST.get('cap', ''),
                'email': request.POST.get('email', ''),
                'sito_web': request.POST.get('sito_web', ''),
                'partita_iva': request.POST.get('partita_iva', None),
            }
            add_client(data)
            messages.success(request, "Client added successfully!")
        return redirect('dashboard')

    if has_editor_permission:
        template = 'dashboard-editor.html'
    elif has_viewer_permission:
        template = 'dashboard-viewer.html'
    else:
        template = 'dashboard-viewer.html'  # Default for no permissions

    return render(request, template, {
        'group_name': group_name,
        'has_viewer_permission': has_viewer_permission,
        'has_editor_permission': has_editor_permission,
    })




class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return redirect('signin')

    def get(self, request):  # Add GET handler
        logout(request)
        return redirect('signin')

def create_user_with_role(username, email, password, role):
    user = User.objects.create_user(username, email, password)
    group = Group.objects.get(name=role)  # 'Editor' or 'Viewer'
    user.groups.add(group)
    user.save()
    return user

# Example usage in SignupView or a custom endpoint
class SignupView(View):
    def post(self, request):
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        role = request.POST.get('role', 'Viewer')  # Default to Viewer
        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'Username taken'})
        user = create_user_with_role(username, email, password, role)
        login(request, user)
        return redirect('/')
