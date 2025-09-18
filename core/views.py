from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import User, Ativo
from .forms import UserForm, AtivoForm  # Supondo que você tenha formulários criados

# ---------------------------
# Listar Todos os Usuários
# ---------------------------
def listar_usuarios(request):
    usuarios = User.objects.all()
    return render(request, 'core/listar_usuarios.html', {'usuarios': usuarios})

# ---------------------------
# Detalhes de um Usuário
# ---------------------------
def detalhes_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    return render(request, 'core/detalhes_usuario.html', {'usuario': usuario})

# ---------------------------
# Criar Novo Usuário
# ---------------------------
def criar_usuario(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_usuarios')  # Redireciona para a lista de usuários
    else:
        form = UserForm()
    
    return render(request, 'core/criar_usuario.html', {'form': form})

# ---------------------------
# Listar Todos os Ativos
# ---------------------------
def listar_ativos(request):
    ativos = Ativo.objects.all()
    return render(request, 'core/listar_ativos.html', {'ativos': ativos})

# ---------------------------
# Detalhes de um Ativo
# ---------------------------
def detalhes_ativo(request, ativo_id):
    ativo = get_object_or_404(Ativo, id=ativo_id)
    return render(request, 'core/detalhes_ativo.html', {'ativo': ativo})

# ---------------------------
# Criar Novo Ativo
# ---------------------------
def criar_ativo(request):
    if request.method == 'POST':
        form = AtivoForm(request.POST)
        if form.is_valid():
            ativo = form.save(commit=False)
            ativo.gerar_qrcode()  # Gera o QR Code automaticamente
            ativo.save()
            return redirect('listar_ativos')  # Redireciona para a lista de ativos
    else:
        form = AtivoForm()
    
    return render(request, 'core/criar_ativo.html', {'form': form})
