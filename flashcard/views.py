from django.shortcuts import render, redirect
from .models import Categoria, FlashCard, Desafio, FlashcardDesafio
from django.contrib.messages import constants
from django.contrib import messages

def novo_flashcard(request):
    if not request.user.is_authenticated:
        return redirect('/usuarios/login')
    
    if request.method == 'GET':
        categorias = Categoria.objects.all()
        dificuldades = FlashCard.DIFICULDADE_CHOICES

        categoria_filter = request.GET.get('categoria')
        dificuldade_filter = request.GET.get('dificuldade')

        if categoria_filter and not dificuldade_filter:
            flashcards = FlashCard.objects.filter(categoria__id = categoria_filter)
        elif  dificuldade_filter and not categoria_filter:
            flashcards = FlashCard.objects.filter(dificuldade = dificuldade_filter)
        elif categoria_filter and dificuldade_filter:
            flashcards = FlashCard.objects.filter(categoria__id = categoria_filter).filter(dificuldade = dificuldade_filter)
        else:
            flashcards = FlashCard.objects.filter(user = request.user)

        return render(request,'novo_flashcard.html', 
                      {'categorias' : categorias, 
                       'dificuldades': dificuldades,
                       'flashcards': flashcards}
                      )
    
    elif request.method == 'POST':
        pergunta = request.POST.get('pergunta')
        resposta = request.POST.get('resposta')
        categoria = request.POST.get('categoria')
        dificuldade = request.POST.get('dificuldade')

        if len(pergunta.strip()) == 0:
            messages.add_message(request, constants.ERROR, 'Informe a pergunta.')
            return redirect('/flashcard/novo_flashcard/')
        if len(resposta.strip()) == 0:
            messages.add_message(request, constants.ERROR, 'Informe uma resposta.')
            return redirect('/flashcard/novo_flashcard/')
        if not categoria:
            messages.add_message(request, constants.ERROR, 'Informe uma categoria.')
            return redirect('/flashcard/novo_flashcard/')
        if not dificuldade:
            messages.add_message(request, constants.ERROR, 'Informe uma dificuldade.')
            return redirect('/flashcard/novo_flashcard/')
        try:
            flashcard = FlashCard(
                user = request.user,
                pergunta = pergunta,
                resposta = resposta,
                categoria_id = categoria,
                dificuldade = dificuldade
            )

            flashcard.save()
            messages.add_message(request, constants.SUCCESS , 'Flashcard cadastrado com sucesso.')
            return redirect('/flashcard/novo_flashcard/')
        except:
            messages.add_message(request, constants.ERROR, 'Erro interno do sistema.')
            return redirect('/flashcard/novo_flashcard/')
        
def deletar_flashcard(request, id):
    flashcard =  FlashCard.objects.get(id = id)
    if flashcard.user != request.user:
        messages.add_message(request, constants.ERROR , f'Flashcard: { flashcard } não pertence ao seu usuário.')
        return redirect('/flashcard/novo_flashcard/')

    flashcard.delete()
    messages.add_message(request, constants.SUCCESS , f'Flashcard: { flashcard } deletado com sucesso.')
    return redirect('/flashcard/novo_flashcard/')

def iniciar_desafio(request):
    if request.method == 'GET':
        categorias = Categoria.objects.all()
        dificuldades = FlashCard.DIFICULDADE_CHOICES

        return render(request, 'iniciar_desafio.html',{
                        'categorias' : categorias, 
                        'dificuldades': dificuldades
                       })
    
    elif request.method == 'POST':
        titulo = request.POST.get('titulo')
        categorias = request.POST.getlist('categoria') # Usado porque o campo na tela 'e do tipo multiple
        dificuldade = request.POST.get('dificuldade')
        qtd_perguntas = request.POST.get('qtd_perguntas')

        flashcards = (
            FlashCard.objects.filter(user =  request.user)
            .filter(dificuldade = dificuldade)
            .filter(categoria_id__in = categorias)
            .order_by('?') # ? ordena de forma aleatoria
        )

        count_flashcards = flashcards.count()
        if count_flashcards < int(qtd_perguntas):
            messages.add_message(request, constants.ERROR , f'Não é possível cadastrar o desafio pois a quantidade de flashcard e menor que {qtd_perguntas}.')
            return redirect('/flashcard/iniciar_desafio/')

        try:
            desafio = Desafio(
                user = request.user,
                titulo = titulo,
                quantidade_perguntas = qtd_perguntas,
                dificuldade = dificuldade
            )

            desafio.save()
            desafio.categoria.add(*categorias) # Inserindo todas as categorias selecionadas
            
            flashcards = flashcards[:int(qtd_perguntas)]

            for fc in flashcards:
                flashcard_desafio = FlashcardDesafio(
                    flashcard = fc
                )
                flashcard_desafio.save()
                desafio.flashcards.add(flashcard_desafio)

            desafio.save()

            return redirect('/flashcard/listar_desafio/')
        except:
            messages.add_message(request, constants.ERROR , 'Erro interno do sistema.')
            return redirect('/flashcard/iniciar_desafio/')
        
def listar_desafio(request):
    if request.method == 'GET':
        categorias = Categoria.objects.all()
        dificuldades = FlashCard.DIFICULDADE_CHOICES

        categoria_filter = request.GET.get('categoria')
        dificuldade_filter = request.GET.get('dificuldade')

        if categoria_filter and not dificuldade_filter:
            desafios = Desafio.objects.filter(user = request.user).filter(categoria__id = categoria_filter)
        elif  dificuldade_filter and not categoria_filter:
            desafios = Desafio.objects.filter(user = request.user).filter(dificuldade = dificuldade_filter)
        elif categoria_filter and dificuldade_filter:
            desafios = Desafio.objects.filter(user = request.user).filter(categoria__id = categoria_filter).filter(dificuldade = dificuldade_filter)
        else:
            desafios = Desafio.objects.filter(user = request.user)

        return render(request,'listar_desafio.html',
                    {
                        'desafios': desafios,
                        'categorias' : categorias, 
                        'dificuldades': dificuldades
                    })
    
def desafio(request, id):
    if request.method == 'GET':
        desafio = Desafio.objects.get(id = id)

        if not desafio.user == request.user:
            return redirect(f'/flashcard/desafio/{id}')
    
        acertos = desafio.flashcards.filter(respondido = True).filter(acertou = True).count()
        erros = desafio.flashcards.filter(respondido = True).filter(acertou = False).count()
        restam = desafio.flashcards.filter(respondido = False).count()
        return render(request,'desafio.html',
                    {
                        'desafio': desafio,
                        'acertos': acertos,
                        'erros': erros,
                        'restam': restam
                    })

def responder_flashcard(request, id):
    flashcard_desafio = FlashcardDesafio.objects.get(id = id)
    acertou = request.GET.get('acertou')
    desafio_id = request.GET.get('desafio_id')

    if not flashcard_desafio.flashcard.user == request.user:
        # messages.add_message(request, constants.ERROR , 'Erro interno do sistema.')
        return redirect(f'/flashcard/desafio/{desafio_id}')

    flashcard_desafio.respondido = True
    flashcard_desafio.acertou = True if acertou == "1" else False
    flashcard_desafio.save()

    return redirect(f'/flashcard/desafio/{desafio_id}')

def relatorio(request, id):

    desafio = Desafio.objects.get(id = id)
    acertos = desafio.flashcards.filter(acertou = True).count()
    erros = desafio.flashcards.filter(acertou = False).count()

    dados = [acertos, erros]

    categorias = desafio.categoria.all()

    name_categorias = [i.nome for i in categorias] # Criando lista de categorias

    dados_categorias = []
    for categoria in categorias:
        dados_categorias.append(desafio.flashcards.filter(flashcard__categoria = categoria).filter(acertou = True).count())

    #TODO: Fazer o Ranking melhores e piores materias

    return render(request, 'relatorio.html', {
                                                'desafio': desafio,
                                                'dados': dados,
                                                'name_categorias': name_categorias,
                                                'dados_categorias': dados_categorias
                                                })