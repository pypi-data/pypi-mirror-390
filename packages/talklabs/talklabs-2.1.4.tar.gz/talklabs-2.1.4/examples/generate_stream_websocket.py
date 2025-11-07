#!/usr/bin/env python3
"""
Exemplo: Streaming WebSocket (RECOMENDADO para textos longos)
Demonstra o uso do método stream_text() que usa WebSocket.
Este método é mais robusto e adequado para textos extensos.
Lê o texto de um arquivo .txt e gera um arquivo .wav com o mesmo nome.
"""
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from talklabs import TalkLabsClient

# Carregar variáveis de ambiente
load_dotenv()

async def exemplo_streaming_websocket():
    """
    Exemplo de streaming WebSocket com o método stream_text().

    Este método usa WebSocket e é RECOMENDADO para textos longos,
    pois tem melhor performance e não tem limitação de tamanho.

    Lê o texto de generate_stream_websocket.txt e salva em generate_stream_websocket.wav
    """
    # Inicializar o cliente com a chave API do .env
    api_key = os.getenv("TALKLABS_API_KEY")
    if not api_key:
        raise ValueError("TALKLABS_API_KEY não encontrada no arquivo .env")

    client = TalkLabsClient(api_key=api_key)

    # Definir o nome do arquivo de entrada e saída
    script_name = Path(__file__).stem  # 'generate_stream_websocket'
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

    print("🎙️  Iniciando streaming WebSocket...")

    # Receber áudio em chunks via streaming WebSocket
    async for chunk in client.stream_text(
        text=text,
        voice=voice,
        language="pt",
        speed=1.0
    ):
        chunks_received.append(chunk)
        print(f"  📦 Chunk {len(chunks_received)} recebido: {len(chunk):,} bytes")

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
    asyncio.run(exemplo_streaming_websocket())
