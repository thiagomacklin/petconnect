from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Animal, Adotante
from django.shortcuts import render, redirect, get_object_or_404
import openai
import json
from django.conf import settings
from openai import OpenAI
import os, re
from django.contrib.auth import authenticate, login, logout


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def index(request):
    animais_destaque = Animal.objects.all().order_by("?")[:3]

    return render(request, "index.html", {
        "animais_destaque": animais_destaque
    })

def como_ajudar(request):
    return render(request, "como-ajudar.html")

def sobre_nos(request):
    return render(request, 'sobre.html')

@login_required
def cadastrar_animal(request):

    if request.method == 'POST':

        fotos = request.FILES.getlist('fotos')

        # 🔥 1. monta perfil IA ANTES de salvar
        perfil_ia = {
            "nivel_energia": request.POST.get('nivel_energia'),
            "necessidade_espaco": request.POST.get('necessidade_espaco'),
            "convive_criancas": request.POST.get('convive_criancas'),
            "convive_animais": request.POST.get('convive_animais'),
            "experiencia_tutor": request.POST.get('experiencia_tutor'),
            "tempo_diario": request.POST.get('tempo_diario'),
            "caracteristicas": request.POST.get('caracteristicas'),
        }

        # 🔥 2. chama IA para gerar código
        codigo_compatibilidade = gerar_codigo_compatibilidade(perfil_ia)

        animal = Animal.objects.create(

            usuario=request.user,

            # básicos
            nome=request.POST.get('nome'),
            idade=request.POST.get('idade'),
            tipo=request.POST.get('tipo'),
            sexo=request.POST.get('sexo'),
            porte=request.POST.get('porte'),
            status=request.POST.get('status'),

            # saúde
            vacinado='vacinado' in request.POST,
            castrado='castrado' in request.POST,
            descricao=request.POST.get('descricao'),

            # perfil IA
            nivel_energia=request.POST.get('nivel_energia') or None,
            necessidade_espaco=request.POST.get('necessidade_espaco') or None,
            convive_criancas=request.POST.get('convive_criancas') or None,
            convive_animais=request.POST.get('convive_animais') or None,
            experiencia_tutor=request.POST.get('experiencia_tutor') or None,
            tempo_diario=request.POST.get('tempo_diario') or None,

            caracteristicas=request.POST.get('caracteristicas'),
            perfil_ia=json.dumps(perfil_ia, ensure_ascii=False),

            # 🔥 gerado pela IA
            codigo_compatibilidade=codigo_compatibilidade,
        )

        # salva até 3 imagens
        if len(fotos) > 0:
            animal.foto1 = fotos[0]

        if len(fotos) > 1:
            animal.foto2 = fotos[1]

        if len(fotos) > 2:
            animal.foto3 = fotos[2]

        animal.save()

        return redirect('listar_animais')

    return render(request, 'animais/cadastrar.html')


def listar_animais(request):

    animais = Animal.objects.all().order_by('-id')

    paginator = Paginator(animais, 6)

    page_number = request.GET.get('page')

    animais = paginator.get_page(page_number)

    return render(request, 'animais/animais.html', {'animais': animais})


@login_required
def editar_animal(request, id):

    # somente administradores
    if not request.user.is_superuser:
        return redirect('listar_animais')

    animal = get_object_or_404(
        Animal,
        id=id
    )

    if request.method == 'POST':

        animal.nome = request.POST.get('nome')
        animal.idade = request.POST.get('idade')
        animal.tipo = request.POST.get('tipo')
        animal.sexo = request.POST.get('sexo')
        animal.porte = request.POST.get('porte')
        animal.status = request.POST.get('status')

        animal.vacinado = 'vacinado' in request.POST
        animal.castrado = 'castrado' in request.POST

        animal.descricao = request.POST.get('descricao')

        # perfil IA
        animal.nivel_energia = request.POST.get('nivel_energia') or None
        animal.necessidade_espaco = request.POST.get('necessidade_espaco') or None
        animal.convive_criancas = request.POST.get('convive_criancas') or None
        animal.convive_animais = request.POST.get('convive_animais') or None
        animal.experiencia_tutor = request.POST.get('experiencia_tutor') or None
        animal.tempo_diario = request.POST.get('tempo_diario') or None

        animal.caracteristicas = request.POST.get(
            'caracteristicas'
        )

        animal.perfil_ia = request.POST.get(
            'perfil_ia'
        )

        animal.codigo_compatibilidade = request.POST.get(
            'codigo_compatibilidade'
        )

        # imagens
        fotos = request.FILES.getlist('fotos')

        if len(fotos) > 0:
            animal.foto1 = fotos[0]

        if len(fotos) > 1:
            animal.foto2 = fotos[1]

        if len(fotos) > 2:
            animal.foto3 = fotos[2]

        animal.save()

        return redirect(
            'listar_animais'
        )

    return render(
        request,
        'animais/editar.html',
        {
            'animal': animal
        }
    )


@login_required
def excluir_animal(request, id):
    animal = get_object_or_404(Animal, id=id)
    animal.delete()
    print('deletei')
    return redirect("listar_animais")


def adotar_animal(request, id):

    animal = get_object_or_404(Animal, id=id)

    if request.method == "POST":

        # =====================================
        # SALVA ADOTANTE
        # =====================================

        adotante = Adotante.objects.create(
            animal=animal,

            nome=request.POST.get("nome"),
            cpf=request.POST.get("cpf"),
            email=request.POST.get("email"),
            telefone=request.POST.get("telefone"),

            residencia=request.POST.get("residencia"),
            quintal=request.POST.get("quintal"),
            criancas=request.POST.get("criancas"),

            experiencia=request.POST.get("experiencia"),
            tempo=request.POST.get("tempo"),
            outros_animais=request.POST.get("outros_animais"),
            perfil=request.POST.get("perfil"),

            descricao=request.POST.get("descricao"),
        )

        # =====================================
        # VALIDAÇÃO LOCAL
        # =====================================

        texto = f"""
        {adotante.perfil}
        {adotante.descricao}
        """.lower()

        palavras_proibidas = [
            "matar",
            "bater",
            "espancar",
            "abandonar",
            "rinha",
            "caçar",
            "caça",
            "veneno",
            "machucar",
            "maltratar",
            "maus tratos",
            "agredir",
            "violência",
        ]

        if any(p in texto for p in palavras_proibidas):

            resultado = {
                "status": "REPROVADO",
                "compatibilidade": 0,
                "risco": "ALTO",
                "justificativa":
                    "Foram identificados termos incompatíveis "
                    "com adoção responsável.",
                "recomendacao":
                    "A adoção não foi aprovada. "
                    "Busque orientação sobre guarda responsável."
            }

        else:

            perfil_animal = f"""
            Nome: {animal.nome}
            Energia: {animal.nivel_energia}
            Espaço: {animal.necessidade_espaco}
            Crianças: {animal.convive_criancas}
            Outros animais: {animal.convive_animais}
            Características: {animal.caracteristicas}
            """

            perfil_adotante = f"""
            Residência: {adotante.residencia}
            Quintal: {adotante.quintal}
            Crianças: {adotante.criancas}
            Experiência: {adotante.experiencia}
            Tempo disponível: {adotante.tempo}
            Outros animais: {adotante.outros_animais}
            Perfil desejado: {adotante.perfil}
            Descrição: {adotante.descricao}
            """

            prompt = f"""
Você é especialista em:

- proteção animal;
- adoção responsável;
- comportamento animal;
- bem-estar animal.

Sua prioridade absoluta é proteger o animal.

Analise os perfis.

Detecte:

- maus-tratos;
- violência;
- abandono;
- negligência;
- exploração;
- rinhas;
- caça;
- agressividade;
- ameaças;
- irresponsabilidade;
- respostas ofensivas;
- respostas aleatórias;
- tentativas de burlar o sistema.

Caso identifique qualquer situação de risco,
a adoção deve ser REPROVADA.

Avalie também:

- compatibilidade comportamental;
- ambiente;
- espaço;
- experiência;
- família;
- tempo disponível;
- capacidade de cuidado.

Retorne APENAS JSON.

Exemplo:

{{
"status":"APROVADO",
"compatibilidade":85,
"risco":"BAIXO",
"justificativa":"texto",
"recomendacao":"texto"
}}

ANIMAL:
{perfil_animal}

ADOTANTE:
{perfil_adotante}
"""

            try:

                client = OpenAI(
                    api_key=os.getenv("OPENAI_API_KEY")
                )

                response = client.chat.completions.create(
                    model="gpt-4o-mini",

                    response_format={
                        "type": "json_object"
                    },

                    temperature=0.2,

                    messages=[
                        {
                            "role": "system",
                            "content":
                                "Você é um especialista em adoção responsável."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )

                resultado = json.loads(
                    response.choices[0].message.content
                )

            except Exception as e:

                print(e)

                resultado = {
                    "status": "REPROVADO",
                    "compatibilidade": 0,
                    "risco": "ALTO",
                    "justificativa":
                        "Não foi possível validar a resposta da IA.",
                    "recomendacao":
                        "Realizar nova avaliação."
                }

        # =====================================
        # SALVA
        # =====================================

        adotante.compatibilidade_nota = resultado.get(
            "compatibilidade",
            0
        )

        adotante.compatibilidade_relatorio = json.dumps(
            resultado,
            ensure_ascii=False,
            indent=2
        )

        adotante.save()

        return render(
            request,
            "animais/adocao.html",
            {
                "animal": animal,
                "compatibilidade": resultado
            }
        )

    return render(
        request,
        "animais/adocao.html",
        {
            "animal": animal
        }
    )


def gerar_codigo_compatibilidade(perfil):
    """
    Função responsável por chamar a OpenAI e gerar o código de compatibilidade.
    """

    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    prompt = f"""
Você é um sistema de adoção de animais.

Com base no perfil abaixo, gere um código curto de compatibilidade (máx 12 caracteres alfanuméricos).

O código deve representar o perfil comportamental do animal de forma única.

Perfil do animal:
{json.dumps(perfil, ensure_ascii=False)}

Responda APENAS com o código.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você gera códigos curtos de compatibilidade."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content.strip()

def gerar_compatibilidade(adotante, animal):
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    prompt = f"""
Você é um sistema de adoção de animais.

Compare o perfil do adotante com o perfil do animal e gere:

1. Um score de compatibilidade de 0 a 100
2. Uma frase curta explicando o resultado

ANIMAL:
{json.dumps({
    "energia": animal.nivel_energia,
    "espaco": animal.necessidade_espaco,
    "criancas": animal.convive_criancas,
    "animais": animal.convive_animais,
    "experiencia_necessaria": animal.experiencia_tutor,
    "tempo": animal.tempo_diario,
    "caracteristicas": animal.caracteristicas,
}, ensure_ascii=False)}

ADOTANTE:
{json.dumps(adotante, ensure_ascii=False)}

Responda no formato:
score: X
mensagem: Y
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você avalia compatibilidade entre adotante e animal."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content


def login_usuario(request):

    erro = None

    if request.method == "POST":

        usuario = request.POST.get("username")
        senha = request.POST.get("password")

        user = authenticate(
            request,
            username=usuario,
            password=senha
        )

        if user:
            login(request, user)
            return redirect("index")
        else:
            erro = "Usuário ou senha inválidos."

    return render(request, "login/login.html", {"erro": erro})


def logout_usuario(request):
    logout(request)
    return redirect("index")