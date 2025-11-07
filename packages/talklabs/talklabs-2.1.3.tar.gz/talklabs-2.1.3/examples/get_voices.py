#!/usr/bin/env python3
"""
Exemplo: Listar Vozes Disponíveis
Demonstra como obter a lista de todas as vozes disponíveis na API.
"""
import json
import os
from dotenv import load_dotenv
from talklabs import TalkLabsClient

# Carregar variáveis de ambiente
load_dotenv()

def exemplo_listar_vozes():
    """
    Exemplo de como listar todas as vozes disponíveis.

    Este método retorna informações detalhadas sobre cada voz,
    incluindo ID, nome, idioma, gênero e outras características.
    """
    # Inicializar o cliente com a chave API do .env
    api_key = os.getenv("TALKLABS_API_KEY")
    if not api_key:
        raise ValueError("TALKLABS_API_KEY não encontrada no arquivo .env")

    client = TalkLabsClient(api_key=api_key)

    # Obter lista de vozes disponíveis
    voices = client.get_voices()

    print(f"📊 Total de vozes disponíveis: {len(voices)}\n")
    print("=" * 60)
    print("VOZES DISPONÍVEIS:")
    print("=" * 60)

    # Listar cada voz com suas características
    for i, voice in enumerate(voices, 1):
        print(f"\n{i}. {voice.get('name', 'N/A')}")
        print(f"   ID: {voice.get('voice_id', 'N/A')}")

        # Mostrar labels (características da voz)
        labels = voice.get('labels', {})
        if labels:
            if 'language' in labels:
                print(f"   Idioma: {labels['language']}")
            if 'gender' in labels:
                print(f"   Gênero: {labels['gender']}")
            if 'accent' in labels:
                print(f"   Sotaque: {labels['accent']}")
            if 'age' in labels:
                print(f"   Idade: {labels['age']}")

        # Mostrar categoria se disponível
        category = voice.get('category')
        if category:
            print(f"   Categoria: {category}")

    # Opcional: Salvar lista completa em JSON
    with open("vozes_disponiveis.json", "w", encoding="utf-8") as f:
        json.dump(voices, f, indent=2, ensure_ascii=False)

    print("\n💾 Lista completa salva em: vozes_disponiveis.json")

    # Exemplo de filtro por idioma
    print("\n" + "=" * 60)
    print("VOZES EM PORTUGUÊS BRASILEIRO:")
    print("=" * 60)

    vozes_pt_br = [
        v for v in voices
        if v.get('labels', {}).get('language') == 'Portuguese'
        or 'pt' in v.get('labels', {}).get('accent', '').lower()
    ]

    for voice in vozes_pt_br:
        print(f"- {voice['name']} (ID: {voice['voice_id']})")

if __name__ == "__main__":
    exemplo_listar_vozes()