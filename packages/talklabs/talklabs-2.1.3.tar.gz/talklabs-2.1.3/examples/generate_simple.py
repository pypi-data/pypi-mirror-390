#!/usr/bin/env python3
"""
Exemplo: Geração Simples (Síncrona)
Demonstra o uso básico do método generate() para síntese de voz.
Lê o texto de um arquivo .txt e gera um arquivo .wav com o mesmo nome.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from talklabs import TalkLabsClient

# Carregar variáveis de ambiente
load_dotenv()

def exemplo_geracao_simples():
    """
    Exemplo básico de geração de áudio com o método generate().

    Este método é síncrono e retorna o áudio completo de uma vez.
    Ideal para textos curtos e quando não há necessidade de streaming.

    Lê o texto de generate_simple.txt e salva em generate_simple.wav
    """
    # Inicializar o cliente com a chave API do .env
    api_key = os.getenv("TALKLABS_API_KEY")
    if not api_key:
        raise ValueError("TALKLABS_API_KEY não encontrada no arquivo .env")

    client = TalkLabsClient(api_key=api_key, timeout=180)

    # Definir o nome do arquivo de entrada e saída
    script_name = Path(__file__).stem  # 'generate_simple'
    script_dir = Path(__file__).parent

    # Ler o texto do arquivo text.txt (compartilhado por todos os exemplos)
    txt_file = script_dir / "text.txt"
    if not txt_file.exists():
        raise FileNotFoundError(f"Arquivo {txt_file} não encontrado. "
                              "Crie o arquivo text.txt na pasta examples/ com o texto para sintetizar.")

    text = txt_file.read_text(encoding='utf-8').strip()
    print(f"📖 Lendo texto de: {txt_file.name}")
    print(f"📝 Tamanho do texto: {len(text)} caracteres")

    # Voz a ser utilizada (veja get_voices.py para listar todas)
    voice = "adam_rocha"  # Voz masculina em português brasileiro

    # Gerar o áudio
    print(f"🎙️  Gerando áudio com a voz '{voice}'...")
    audio_bytes = client.generate(
        text=text,
        voice=voice,
        language="pt",  # Idioma: português
        speed=1.0       # Velocidade normal (0.5 a 2.0)
    )

    # Salvar o áudio em arquivo com o mesmo nome
    output_file = script_dir / f"{script_name}.wav"
    with open(output_file, "wb") as f:
        f.write(audio_bytes)

    print(f"✅ Áudio salvo em: {output_file.name}")
    print(f"📊 Tamanho: {len(audio_bytes):,} bytes")

if __name__ == "__main__":
    exemplo_geracao_simples()