from openai import OpenAI
import json

client = OpenAI(api_key="SUA_API_KEY_AQUI")


def gerar_codigo_compatibilidade(perfil: dict):
    """
    Gera um código de compatibilidade baseado no perfil do animal
    """

    prompt = f"""
Você é um sistema de adoção de animais.

Com base no perfil abaixo, gere um código de compatibilidade curto (máx 10 caracteres alfanuméricos).

O código deve representar o tipo de animal e perfil comportamental.

Perfil:
{json.dumps(perfil, indent=2, ensure_ascii=False)}

Responda APENAS com o código.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    )

    return response.choices[0].message.content.strip()