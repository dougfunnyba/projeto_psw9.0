from django.shortcuts import render, redirect
from django.contrib.messages import constants
from django.contrib import messages
from .models import Apostila, ViewApostila

def adicionar_apostilas(request):
    if request.method == 'GET':
        apostilas = Apostila.objects.filter(user = request.user)

        views_totais = ViewApostila.objects.filter(apostila__user = request.user).count()

        return render(request, 'adicionar_apostilas.html', 
                        {
                            'apostilas': apostilas,
                            'views_totais': views_totais 
                        }
                      )
    
    elif request.method == 'POST':
        titulo = request.POST.get('titulo')
        arquivo = request.FILES.get('arquivo')

        if not titulo.strip():
            messages.add_message(request, constants.ERROR, 'Título obrigatório.')
            return redirect('/apostilas/adicionar_apostilas/')
        
        if not arquivo:
            messages.add_message(request, constants.ERROR, 'Informe um arquivo para fazer o upload.')
            return redirect('/apostilas/adicionar_apostilas/')
        
        try:
            apostila = Apostila(
                user = request.user,
                titulo = titulo,
                arquivo = arquivo
            )
            apostila.save()
            messages.add_message(request, constants.SUCCESS, 'Arquivo salvo com sucesso.')
            return redirect('/apostilas/adicionar_apostilas/')
        except:
            messages.add_message(request, constants.ERROR, 'Erro interno do sistema.')
            return redirect('/apostilas/adicionar_apostilas/')
        
def apostila(request, id):
    apostila = Apostila.objects.get(id = id)

    view = ViewApostila(
        ip = request.META['REMOTE_ADDR'],
        apostila = apostila
    )
    view.save()

    views_totais = ViewApostila.objects.filter(apostila = apostila).count()
    views_unicas =  ViewApostila.objects.filter(apostila = apostila).values('ip').distinct().count()

    return render(request, 'apostila.html', 
                    {
                        'apostila': apostila,
                        'views_totais': views_totais,
                        'views_unicas': views_unicas
                    }
                )