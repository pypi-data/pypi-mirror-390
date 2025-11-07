#!/usr/bin/env python3
"""
Exemplo: Streaming HTTP
Demonstra o uso do método generate_stream() para receber áudio em chunks via HTTP.
Lê o texto de um arquivo .txt e gera um arquivo .wav com o mesmo nome.

⚠️ AVISO IMPORTANTE:
Este método (generate_stream via HTTP) tem limitações com textos longos.
Para textos extensos (> 1000 caracteres), recomenda-se usar o método WebSocket.

Veja: examples/generate_stream_websocket.py
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from talklabs import TalkLabsClient

# Carregar variáveis de ambiente
load_dotenv()

def exemplo_streaming_http():
    """
    Exemplo de streaming HTTP com o método generate_stream().

    Este método retorna o áudio em chunks progressivamente via HTTP.
    Útil quando você quer começar a processar o áudio antes de ter o arquivo completo.

    Lê o texto de generate_stream.txt e salva em generate_stream.wav
    """
    # Inicializar o cliente com a chave API do .env
    api_key = os.getenv("TALKLABS_API_KEY")
    if not api_key:
        raise ValueError("TALKLABS_API_KEY não encontrada no arquivo .env")

    client = TalkLabsClient(api_key=api_key)

    # Definir o nome do arquivo de entrada e saída
    script_name = Path(__file__).stem  # 'generate_stream'
    script_dir = Path(__file__).parent

    # Ler o texto do arquivo text.txt (compartilhado por todos os exemplos)
    txt_file = script_dir / "text.txt"
    if not txt_file.exists():
        raise FileNotFoundError(f"Arquivo {txt_file} não encontrado. "
                              "Crie o arquivo text.txt na pasta examples/ com o texto para sintetizar.")

    text = txt_file.read_text(encoding='utf-8').strip()
    print(f"📖 Lendo texto de: {txt_file.name}")
    print(f"📝 Tamanho do texto: {len(text)} caracteres")

    # Voz a ser utilizada
    voice = "adam_rocha"  # Voz masculina em português brasileiro

    # Coletar chunks durante o streaming
    chunks_received = []

    # Receber áudio em chunks via streaming HTTP
    print(f"🎙️  Gerando áudio com streaming HTTP...")
    for chunk in client.generate_stream(
        text=text,
        voice=voice,
        language="pt",
        speed=1.0
    ):
        chunks_received.append(chunk)
        print(f"  📦 Chunk recebido: {len(chunk):,} bytes")
        # Aqui você poderia processar cada chunk conforme recebe
        # Por exemplo, enviar para um player de áudio ou buffer

    # Juntar todos os chunks
    full_audio = b"".join(chunks_received)

    # Salvar o áudio completo com o mesmo nome
    output_file = script_dir / f"{script_name}.wav"
    with open(output_file, "wb") as f:
        f.write(full_audio)

    print(f"\n✅ Áudio salvo em: {output_file.name}")
    print(f"📊 Total de chunks: {len(chunks_received)}")
    print(f"📊 Tamanho total: {len(full_audio):,} bytes")

if __name__ == "__main__":
    exemplo_streaming_http()