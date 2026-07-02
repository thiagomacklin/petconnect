from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver


class Animal(models.Model):

    TIPO_CHOICES = [
        ('CAO', 'Cachorro'),
        ('GATO', 'Gato'),
    ]

    SEXO_CHOICES = [
        ('M', 'Macho'),
        ('F', 'Fêmea'),
    ]

    PORTE_CHOICES = [
        ('P', 'Pequeno'),
        ('M', 'Médio'),
        ('G', 'Grande'),
    ]

    STATUS_CHOICES = [
        ('DISPONIVEL', 'Disponível para adoção'),
        ('TRATAMENTO', 'Em tratamento'),
        ('ADOTADO', 'Adotado'),
    ]

    NIVEL_CHOICES = [
        (1, 'Baixo'),
        (2, 'Médio'),
        (3, 'Alto'),
    ]

    CONVIVENCIA_CHOICES = [
        (1, 'Não'),
        (2, 'Depende'),
        (3, 'Sim'),
    ]

    EXPERIENCIA_CHOICES = [
        (1, 'Iniciante'),
        (2, 'Intermediário'),
        (3, 'Experiente'),
    ]

    # =================================
    # CONTROLE
    # =================================
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='animais'
    )

    data_cadastro = models.DateTimeField(
        auto_now_add=True
    )

    # =================================
    # DADOS BÁSICOS
    # =================================
    nome = models.CharField(
        max_length=100
    )

    idade = models.CharField(
        max_length=30
    )

    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES
    )

    sexo = models.CharField(
        max_length=1,
        choices=SEXO_CHOICES
    )

    porte = models.CharField(
        max_length=1,
        choices=PORTE_CHOICES
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DISPONIVEL'
    )

    # =================================
    # SAÚDE
    # =================================
    vacinado = models.BooleanField(
        default=False
    )

    castrado = models.BooleanField(
        default=False
    )

    descricao = models.TextField()

    # =================================
    # IMAGENS
    # =================================
    foto1 = models.ImageField(
        upload_to='animais/',
        blank=True,
        null=True
    )

    foto2 = models.ImageField(
        upload_to='animais/',
        blank=True,
        null=True
    )

    foto3 = models.ImageField(
        upload_to='animais/',
        blank=True,
        null=True
    )

    # =================================
    # PERFIL IA
    # =================================
    nivel_energia = models.IntegerField(
        choices=NIVEL_CHOICES,
        null=True,
        blank=True
    )

    necessidade_espaco = models.IntegerField(
        choices=NIVEL_CHOICES,
        null=True,
        blank=True
    )

    convive_criancas = models.IntegerField(
        choices=CONVIVENCIA_CHOICES,
        null=True,
        blank=True
    )

    convive_animais = models.IntegerField(
        choices=CONVIVENCIA_CHOICES,
        null=True,
        blank=True
    )

    experiencia_tutor = models.IntegerField(
        choices=EXPERIENCIA_CHOICES,
        null=True,
        blank=True
    )

    tempo_diario = models.IntegerField(
        choices=NIVEL_CHOICES,
        null=True,
        blank=True
    )

    caracteristicas = models.TextField(
        blank=True
    )

    perfil_ia = models.TextField(
        blank=True
    )

    codigo_compatibilidade = models.CharField(
        max_length=255,
        blank=True
    )

    def __str__(self):
        return self.nome
    

class Adotante(models.Model):

    animal = models.ForeignKey('Animal', on_delete=models.CASCADE)

    nome = models.CharField(max_length=200)
    cpf = models.CharField(max_length=14)
    email = models.EmailField()
    telefone = models.CharField(max_length=20)

    residencia = models.CharField(max_length=50, blank=True, null=True)
    quintal = models.CharField(max_length=10, blank=True, null=True)
    criancas = models.CharField(max_length=10, blank=True, null=True)

    experiencia = models.CharField(max_length=50, blank=True, null=True)
    tempo = models.CharField(max_length=50, blank=True, null=True)
    outros_animais = models.CharField(max_length=10, blank=True, null=True)
    perfil = models.CharField(max_length=50, blank=True, null=True)

    descricao = models.TextField(blank=True, null=True)

    # ✔ IA
    compatibilidade_nota = models.IntegerField(blank=True, null=True)
    compatibilidade_relatorio = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome
    
    
@receiver(pre_save, sender=Animal)
def apagar_imagem_antiga(sender, instance, **kwargs):

    if not instance.pk:
        return

    try:
        animal_antigo = Animal.objects.get(pk=instance.pk)
    except Animal.DoesNotExist:
        return

    campos = ['foto1', 'foto2', 'foto3']

    for campo in campos:
        foto_antiga = getattr(animal_antigo, campo)
        foto_nova = getattr(instance, campo)

        if foto_antiga and foto_antiga != foto_nova:
            foto_antiga.delete(save=False)


@receiver(post_delete, sender=Animal)
def apagar_imagens(sender, instance, **kwargs):

    campos = ['foto1', 'foto2', 'foto3']

    for campo in campos:
        foto = getattr(instance, campo)

        if foto:
            foto.delete(save=False)