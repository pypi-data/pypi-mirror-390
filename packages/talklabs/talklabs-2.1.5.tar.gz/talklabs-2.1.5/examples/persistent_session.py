#!/usr/bin/env python3
"""
Exemplo: Sessão Persistente WebSocket
Demonstra o uso de sessões persistentes para múltiplas sínteses com uma única conexão.
Este é o método mais eficiente para aplicações que precisam sintetizar múltiplos textos.
"""
import asyncio
import os
from dotenv import load_dotenv
from talklabs import TalkLabsClient

# Carregar variáveis de ambiente
load_dotenv()

async def exemplo_sessao_persistente():
    """
    Exemplo de sessão persistente com reutilização de conexão WebSocket.

    VANTAGENS:
    - Uma única conexão para múltiplas sínteses
    - Menor latência (sem overhead de reconexão)
    - Keep-alive automático mantém conexão viva
    - Ideal para chatbots e aplicações interativas
    """
    # Inicializar o cliente com a chave API do .env
    api_key = os.getenv("TALKLABS_API_KEY")
    if not api_key:
        raise ValueError("TALKLABS_API_KEY não encontrada no arquivo .env")

    client = TalkLabsClient(api_key=api_key)

    # Lista de mensagens para sintetizar
    mensagens = [
        "Olá! Bem-vindo ao suporte técnico.",
        "Como posso ajudar você hoje?",
        "Vou verificar isso para você. Um momento, por favor.",
        "Encontrei a solução. Vou explicar o procedimento.",
        "Obrigado por entrar em contato. Tenha um ótimo dia!"
    ]

    # Configurações da sessão
    voice = "adam_rocha"

    session = None

    try:
        # Criar sessão persistente (UMA VEZ)
        print("🔌 Criando sessão persistente...")
        session = await client.create_session(
            voice=voice,
            language="pt",
            speed=1.0,
            ping_interval=20.0,   # Ping a cada 20 segundos
            ping_timeout=20.0     # Timeout após 20 segundos sem resposta
        )
        print("✅ Sessão conectada!\n")

        # Processar cada mensagem usando a MESMA sessão
        for i, mensagem in enumerate(mensagens, 1):
            print(f"[{i}/{len(mensagens)}] Sintetizando: {mensagem}")

            chunks_received = []

            # Usar a sessão existente (sem reconectar)
            async for chunk in session.stream_text(mensagem):
                chunks_received.append(chunk)
                # Em produção, você enviaria cada chunk para o player de áudio

            # Juntar chunks e salvar
            full_audio = b"".join(chunks_received)
            filename = f"sessao_output_{i}.wav"

            with open(filename, "wb") as f:
                f.write(full_audio)

            print(f"[{i}/{len(mensagens)}] ✅ Salvo em: {filename}")
            print(f"[{i}/{len(mensagens)}] 📊 Tamanho: {len(full_audio):,} bytes\n")

            # Simular intervalo entre mensagens (a sessão permanece viva)
            if i < len(mensagens):
                await asyncio.sleep(1)  # Aguardar 1 segundo

        print("=" * 60)
        print("RESUMO:")
        print(f"✅ {len(mensagens)} mensagens sintetizadas")
        print("🔄 Zero reconexões (uma conexão para todas!)")
        print("⚡ Economia de latência significativa")

    except Exception as e:
        print(f"❌ Erro: {e}")
        raise

    finally:
        # IMPORTANTE: Sempre fechar a sessão quando terminar
        if session:
            print("\n🔌 Fechando sessão...")
            await session.close()
            print("✅ Sessão fechada!")

async def exemplo_sessao_com_interacao():
    """
    Exemplo simulando uma interação real de chatbot.
    Mostra como manter a sessão viva entre interações do usuário.
    """
    # Inicializar o cliente com a chave API do .env
    api_key = os.getenv("TALKLABS_API_KEY")
    if not api_key:
        raise ValueError("TALKLABS_API_KEY não encontrada no arquivo .env")

    client = TalkLabsClient(api_key=api_key)

    # Simulação de diálogo
    dialogo = [
        {"tipo": "bot", "texto": "Olá! Sou seu assistente virtual."},
        {"tipo": "usuario", "texto": "[Usuário digita...]", "delay": 2},
        {"tipo": "bot", "texto": "Entendi sua dúvida. Deixe-me explicar."},
        {"tipo": "usuario", "texto": "[Usuário responde...]", "delay": 1.5},
        {"tipo": "bot", "texto": "Perfeito! Problema resolvido. Algo mais?"},
        {"tipo": "usuario", "texto": "[Usuário agradece...]", "delay": 1},
        {"tipo": "bot", "texto": "Foi um prazer ajudar. Até logo!"}
    ]

    session = None
    voice = "adam_rocha"

    try:
        # Criar sessão no início da conversa
        session = await client.create_session(voice=voice, language="pt")
        print("💬 Iniciando conversa com assistente virtual...\n")

        for item in dialogo:
            if item["tipo"] == "bot":
                print(f"🤖 Bot: {item['texto']}")

                # Sintetizar resposta do bot
                chunks = []
                async for chunk in session.stream_text(item["texto"]):
                    chunks.append(chunk)

                audio = b"".join(chunks)
                # Em produção, reproduziria o áudio aqui
                print(f"   🔊 Áudio gerado: {len(audio):,} bytes")

            else:  # usuário
                print(f"👤 Usuário: {item['texto']}")
                # Simular tempo de digitação/resposta do usuário
                await asyncio.sleep(item.get("delay", 1))

            print()  # Linha em branco entre interações

        print("💬 Conversa finalizada!")

    finally:
        if session:
            await session.close()

if __name__ == "__main__":
    print("=" * 60)
    print("EXEMPLO 1: Múltiplas Sínteses com Sessão Persistente")
    print("=" * 60 + "\n")

    # Executar primeiro exemplo
    asyncio.run(exemplo_sessao_persistente())

    print("\n" + "=" * 60)
    print("EXEMPLO 2: Simulação de Chatbot Interativo")
    print("=" * 60 + "\n")

    # Executar segundo exemplo
    asyncio.run(exemplo_sessao_com_interacao())