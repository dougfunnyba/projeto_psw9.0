from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib import auth


def logar(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        user = auth.authenticate(request, username =  username, password = senha)
        if user:
            auth.login(request, user)
            messages.add_message(request, constants.SUCCESS, 'Logado.')
            return redirect(request, '/flashcard/novo_flashcard')
        else:
             messages.add_message(request, constants.ERROR, 'Usuario ou senha invalidos.')
             return redirect('/usuarios/login')
        
def logout(request):
    auth.logout(request)
    return redirect('/usuarios/login')

def cadastro(request):
    if request.method == 'GET':
        return render(request, 'cadastro.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        if not senha == confirmar_senha:
            messages.add_message(request, constants.ERROR, 'Senha e confirmar senha diferentes.')
            return redirect('/usuarios/cadastro')
        
        if User.objects.filter(username = username).exists():
            messages.add_message(request, constants.ERROR, 'Usuario ja existe no sistema.')
            return redirect('/usuarios/cadastro')
        
        try:
            User.objects.create_user(
                username = username,
                password = senha
            )
            return redirect('/usuarios/login')
        except:
            messages.add_message(request, constants.ERROR, 'Erro interno do servidor.')
            return redirect('/usuarios/cadastro')