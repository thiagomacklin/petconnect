from django.contrib import admin
from .models import Animal, Adotante


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'nome',
        'tipo',
        'sexo',
        'porte',
        'status',
        'usuario',
        'vacinado',
        'castrado',
        'data_cadastro',
    )

    list_filter = (
        'tipo',
        'sexo',
        'porte',
        'status',
        'vacinado',
        'castrado',
    )

    search_fields = (
        'nome',
        'descricao',
        'caracteristicas',
        'usuario__username',
    )

    readonly_fields = (
        'data_cadastro',
    )

    fieldsets = (

        ('Informações básicas', {
            'fields': (
                'usuario',
                'nome',
                'idade',
                'tipo',
                'sexo',
                'porte',
                'status',
            )
        }),

        ('Saúde', {
            'fields': (
                'vacinado',
                'castrado',
                'descricao',
            )
        }),

        ('Fotos', {
            'fields': (
                'foto1',
                'foto2',
                'foto3',
            )
        }),

        ('Perfil IA', {
            'fields': (
                'nivel_energia',
                'necessidade_espaco',
                'convive_criancas',
                'convive_animais',
                'experiencia_tutor',
                'tempo_diario',
                'caracteristicas',
                'perfil_ia',
                'codigo_compatibilidade',
            )
        }),

        ('Controle', {
            'fields': (
                'data_cadastro',
            )
        }),
    )



@admin.register(Adotante)
class AdotanteAdmin(admin.ModelAdmin):

    list_display = (
        "nome",
        "animal",
        "email",
        "telefone",
        "compatibilidade_nota",
        "created_at",
    )

    list_filter = (
        "compatibilidade_nota",
        "animal",
    )

    search_fields = (
        "nome",
        "cpf",
        "email",
        "animal__nome",
    )

    readonly_fields = (
        "compatibilidade_nota",
        "compatibilidade_relatorio",
        "created_at",
    )

    fieldsets = (
        ("Dados do adotante", {
            "fields": (
                "animal",
                "nome",
                "cpf",
                "email",
                "telefone",
            )
        }),

        ("Perfil da família", {
            "fields": (
                "residencia",
                "quintal",
                "criancas",
                "experiencia",
                "tempo",
                "outros_animais",
                "perfil",
                "descricao",
            )
        }),

        ("IA de compatibilidade", {
            "fields": (
                "compatibilidade_nota",
                "compatibilidade_relatorio",
            )
        }),
    )