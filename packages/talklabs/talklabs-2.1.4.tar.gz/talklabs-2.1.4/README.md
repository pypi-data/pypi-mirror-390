# 🐍 TalkLabs Python SDK

<div align="center">

**SDK oficial da TalkLabs para síntese de voz com streaming ultra-baixa latência**

[![PyPI version](https://badge.fury.io/py/talklabs.svg)](https://badge.fury.io/py/talklabs)
[![Python versions](https://img.shields.io/pypi/pyversions/talklabs.svg)](https://pypi.org/project/talklabs/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[🚀 Quick Start](#uso-rápido) •
[📚 Documentação](#api-reference) •
[💡 Exemplos](#exemplos-práticos) •
[🆘 Suporte](#suporte)

</div>

---

🚀 **v2.1.4**: Streaming com latência de ~200-500ms + Sessões Persistentes + Fix WAV Header!

## Características

- ✅ **Compatível com ElevenLabs**: Drop-in replacement para APIs existentes
- ⚡ **Ultra-Low Latency**: ~200-500ms até primeiro áudio (vs 5-10s tradicional)
- 🧠 **Processamento Inteligente**: Segmentação natural avançada
- 📡 **Streaming Otimizado**: Sistema paralelo com 3 níveis de prioridade
- 🎧 **Real-time Playback**: Chunks de áudio prontos para reprodução imediata
- 🔄 **Incremental Streaming**: Envio palavra-por-palavra para máxima responsividade

## Instalação

```bash
pip install talklabs
```

## Uso Rápido

### 1. Geração Simples (Síncrona)

```python
from talklabs import TalkLabsClient

client = TalkLabsClient(api_key="tlk_live_xxxxx")

audio = client.generate(
    text="Olá! Bem-vindo ao TalkLabs.",
    voice="adam_rocha",
    language="pt",
    speed=1.0
)

with open("output.wav", "wb") as f:
    f.write(audio)
```

> **Exemplo completo:** Veja [examples/generate_simple.py](examples/generate_simple.py) que lê o texto de um arquivo `text.txt` e salva o áudio com o nome do script.

### 2. 🚀 Streaming WebSocket (Ultra-Low Latency)

```python
import asyncio
from talklabs import TalkLabsClient

async def stream_example():
    client = TalkLabsClient(api_key="tlk_live_xxxxx")

    # Coletar chunks durante o streaming
    chunks = []

    # Streaming via WebSocket (latência ~200-500ms)
    async for audio_chunk in client.stream_text(
        text="Este é um teste de ultra baixa latência!",
        voice="adam_rocha",
        language="pt",
        speed=1.0
    ):
        chunks.append(audio_chunk)
        print(f"Chunk recebido: {len(audio_chunk)} bytes")

    # Juntar e salvar
    full_audio = b"".join(chunks)
    with open("output.wav", "wb") as f:
        f.write(full_audio)

asyncio.run(stream_example())
```

> **Exemplo completo:** Veja [examples/generate_stream_websocket.py](examples/generate_stream_websocket.py) com tratamento de arquivos e progresso detalhado.

### 3. Sessão Persistente (RECOMENDADO para Produção)

```python
import asyncio
from talklabs import TalkLabsClient

async def persistent_session_example():
    client = TalkLabsClient(api_key="tlk_live_xxxxx")

    # Criar sessão persistente (mantém conexão aberta)
    session = await client.create_session(
        voice="adam_rocha",
        language="pt",
        speed=1.0,
        ping_interval=20.0,
        ping_timeout=20.0
    )

    try:
        # Múltiplas sínteses na mesma sessão (sem reconectar)
        for text in ["Primeira frase.", "Segunda frase.", "Terceira frase."]:
            chunks = []
            async for audio_chunk in session.stream_text(text):
                chunks.append(audio_chunk)
                print(f"Chunk: {len(audio_chunk)} bytes")

            # Salvar cada áudio
            full_audio = b"".join(chunks)
            # ... processar ou salvar áudio
    finally:
        # IMPORTANTE: Sempre fechar a sessão
        await session.close()

asyncio.run(persistent_session_example())
```

> **Exemplo completo:** Veja [examples/persistent_session.py](examples/persistent_session.py) com dois exemplos: múltiplas sínteses sequenciais e simulação de chatbot interativo.

### 4. Streaming HTTP (Método Alternativo)

⚠️ **ATENÇÃO**: O método `generate_stream()` via HTTP pode ter limitações com textos muito longos. Para textos extensos (> 1000 caracteres), **use o método WebSocket `stream_text()`** (exemplo #2 acima).

```python
from talklabs import TalkLabsClient

client = TalkLabsClient(api_key="tlk_live_xxxxx")

chunks = []

# Streaming tradicional via HTTP (recomendado apenas para textos curtos)
for chunk in client.generate_stream(
    text="Streaming HTTP incremental",
    voice="adam_rocha",
    language="pt",
    speed=1.0
):
    chunks.append(chunk)
    print(f"Chunk recebido: {len(chunk)} bytes")

# Juntar e salvar
full_audio = b"".join(chunks)
with open("output.wav", "wb") as f:
    f.write(full_audio)
```

> **Exemplo completo:** Veja [examples/generate_stream.py](examples/generate_stream.py)

## API Reference

### `TalkLabsClient`

#### Métodos Principais

**`generate(text, voice, **kwargs)` → bytes**
- Geração síncrona completa via HTTP
- Retorna áudio WAV completo
- Útil para textos curtos e testes simples
- **Parâmetros**:
  - `text`: Texto para sintetizar
  - `voice`: ID da voz (ex: "adam_rocha", "adam_rocha")
  - `language`: Idioma ("pt", "en", "es", etc) - padrão: "pt"
  - `speed`: Velocidade (0.5-2.0) - padrão: 1.0
  - `voice_settings`: Configurações opcionais de voz

**`generate_stream(text, voice, **kwargs)` → Iterator[bytes]**
- Streaming HTTP tradicional
- Retorna chunks progressivamente via HTTP
- ⚠️ **Limitação**: Pode processar apenas textos curtos (< 1000 caracteres). Para textos longos, use `stream_text()`
- Alternativa quando WebSocket não está disponível
- **Parâmetros**: mesmos do `generate()`

**`stream_text(text, voice, **kwargs)` → AsyncIterator[bytes]** ⚡ RECOMENDADO
- Streaming via WebSocket com ultra-baixa latência (~200-500ms)
- Conexão one-shot (abre e fecha para cada síntese)
- Retorna chunks de áudio conforme são gerados
- **Parâmetros**: mesmos do `generate()`

**`create_session(voice, **kwargs)` → StreamingSession** 🎯 MELHOR PARA PRODUÇÃO
- Cria sessão persistente que mantém conexão WebSocket aberta
- Ideal para múltiplas sínteses sem overhead de reconexão
- **Parâmetros**:
  - `voice`: ID da voz para a sessão
  - `language`: Idioma padrão da sessão
  - `speed`: Velocidade padrão
  - `voice_settings`: Configurações de voz
  - `ping_interval`: Intervalo de keep-alive (padrão: 20s)
  - `ping_timeout`: Timeout do keep-alive (padrão: 20s)

**`get_voices()` → list**
- Lista todas as vozes disponíveis
- Retorna array com metadados de cada voz

### Utilitários

**`fix_wav_header(audio_data: bytes)` → bytes**
- Corrige headers WAV após streaming
- Durante streaming, o header pode ter tamanho indefinido (0xFFFFFFFF)
- Esta função recalcula e atualiza os tamanhos corretos
- **Uso recomendado** ao salvar áudios de streaming:

```python
from talklabs import TalkLabsClient, fix_wav_header
import asyncio

async def save_streamed_audio():
    client = TalkLabsClient(api_key="tlk_live_xxxxx")

    # Coletar chunks do streaming
    chunks = []
    async for chunk in client.stream_text(
        text="Este é um texto longo que será transmitido em partes...",
        voice="adam_rocha"
    ):
        chunks.append(chunk)

    # Concatenar todos os chunks
    full_audio = b"".join(chunks)

    # Corrigir o header WAV (IMPORTANTE para playback correto)
    full_audio = fix_wav_header(full_audio)

    # Salvar o arquivo
    with open("output.wav", "wb") as f:
        f.write(full_audio)

asyncio.run(save_streamed_audio())
```

**Por que usar fix_wav_header()?**
- Garante compatibilidade com todos os media players
- Corrige markers de tamanho indefinido do streaming
- Previne erros de "arquivo corrompido" ou "duração incorreta"
- Obrigatório para textos longos que geram áudios > 20MB

### Vozes Disponíveis

```python
# Listar todas as vozes
voices = client.get_voices()
for voice in voices:
    print(f"{voice['voice_id']}: {voice['name']}")
```

**Vozes Populares**:
- `adam_rocha` - Português (BR) - Feminina
- `adam_rocha` - Português (BR) - Masculina
- `maria_silva` - Português (PT) - Feminina
- `joao_santos` - Português (PT) - Masculina

### `StreamingSession`

Classe para sessões persistentes. Métodos disponíveis:

**`stream_text(text)` → AsyncIterator[bytes]**
- Sintetiza texto usando a sessão existente
- Não reconecta, usa WebSocket já aberto
- Mesma assinatura do método principal

**`close()`**
- Fecha a conexão WebSocket
- Sempre chame ao terminar de usar a sessão

**Exemplo com context manager:**
```python
async with await client.create_session(voice="adam_rocha") as session:
    async for chunk in session.stream_text("Olá!"):
        process(chunk)
    # close() é chamado automaticamente
```

## Arquitetura do Streaming Otimizado

### Como Funciona

1. **Segmentação Inteligente**: Texto é dividido em sentenças naturais
2. **Sistema de Filas**: Chunks são processados com prioridades:
   - **P1 (Alta)**: Primeira sentença - processada imediatamente
   - **P2 (Média)**: Sentenças intermediárias
   - **P3 (Baixa)**: Última sentença
3. **Processamento Paralelo**: TTS processa chunks simultaneamente
4. **Streaming Real-time**: Áudio retorna conforme é gerado

### Benefícios

- ⚡ **Latência 95% menor**: ~200-500ms vs 5-10s
- 🎯 **Primeira Palavra Rápida**: Usuário ouve resposta quase instantânea
- 📊 **Escalável**: Suporta múltiplas sessões simultâneas
- 🧠 **Inteligente**: Quebras naturais de sentença garantidas

## 💡 Exemplos Práticos

### Exemplos Disponíveis

Confira nossos exemplos completos na pasta `examples/`:

- **`generate_simple.py`** - Geração síncrona simples
- **`generate_stream.py`** - Streaming HTTP (para textos curtos)
- **`generate_stream_websocket.py`** - Streaming WebSocket (ultra-baixa latência, recomendado para textos longos)
- **`persistent_session.py`** - Sessões persistentes (recomendado para produção)
- **`get_voices.py`** - Listar vozes disponíveis

**Nota:** Todos os exemplos leem o texto de um arquivo `text.txt` compartilhado e geram arquivos `.wav` com o nome correspondente ao script.

### Exemplo: Salvar Chunks Progressivamente

```python
async def save_streaming():
    client = TalkLabsClient(api_key="tlk_live_xxxxx")

    with open("output_streaming.wav", "wb") as f:
        async for chunk in client.stream_text(
            text="Este áudio será salvo em tempo real.",
            voice="adam_rocha"
        ):
            f.write(chunk)

    print("Áudio salvo!")

asyncio.run(save_streaming())
```

### Reprodução em Tempo Real com pyaudio

```python
import pyaudio
import asyncio
from talklabs import TalkLabsClient

async def play_realtime():
    client = TalkLabsClient(api_key="tlk_live_xxxxx")

    # Inicializar pyaudio
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=24000, output=True)

    try:
        async for chunk in client.stream_text(
            text="Olá! Este áudio está sendo reproduzido em tempo real.",
            voice="adam_rocha"
        ):
            # Reproduzir imediatamente
            stream.write(chunk)
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

asyncio.run(play_realtime())
```

### Configurações Avançadas de Voz

```python
from talklabs import TalkLabsClient, VoiceSettings

client = TalkLabsClient(api_key="tlk_live_xxxxx")

settings = VoiceSettings(
    stability=0.85,           # Estabilidade da voz (0-1)
    similarity_boost=0.75,    # Similaridade com voz original
    style=0.0,                # Estilo expressivo (0-1)
    use_speaker_boost=True    # Boost de clareza
)

audio = client.generate(
    text="Teste com configurações customizadas",
    voice="adam_rocha",
    voice_settings=settings,
    speed=1.2  # 20% mais rápido
)
```

## Compatibilidade com ElevenLabs

Este SDK é 100% compatível com o SDK da ElevenLabs. Basta trocar:

```python
# ElevenLabs
from elevenlabs import ElevenLabs
client = ElevenLabs(api_key="...")

# TalkLabs (drop-in replacement)
from talklabs import TalkLabsClient
client = TalkLabsClient(api_key="tlk_live_...")
```

## Limites e Validações

### Limites de Tamanho de Texto

A API TalkLabs implementa limites para garantir performance e prevenir abusos:

| Endpoint | Limite Máximo | Erro Retornado |
|----------|---------------|----------------|
| **HTTP** (`generate`, `generate_stream`) | 50.000 caracteres | HTTP 400/422 |
| **WebSocket** (`stream_text`, sessões) | 10.000 caracteres/mensagem | WebSocket Error |
| **Buffer WebSocket** (acumulado) | 50.000 caracteres | WebSocket Error |
| **Modelo XTTS2** (limite interno por chunk) | ~200 caracteres (400 tokens) | AssertionError |

⚠️ **IMPORTANTE**: O modelo XTTS2 tem um limite interno de **400 tokens por síntese** (~200-203 caracteres em português). A API divide automaticamente textos longos em chunks menores, mas chunks individuais que excedam esse limite causarão erro.

### Validações de Conteúdo

A API valida automaticamente:

- ✅ Texto não pode estar vazio
- ✅ Texto não pode conter apenas espaços
- ✅ Texto não pode conter apenas pontuação (ex: `"..."`, `"???"`)
- ✅ Texto deve conter ao menos um caractere alfanumérico

### Exemplos de Erros

```python
# ❌ Texto muito longo (> 50k)
try:
    client.generate(text="A" * 50001, voice="adam_rocha")
except Exception as e:
    print(e)  # "Text too long (50001 characters). Maximum allowed: 50,000 characters."

# ❌ Texto vazio
try:
    client.generate(text="", voice="adam_rocha")
except Exception as e:
    print(e)  # "Text cannot be empty"

# ❌ Apenas pontuação
try:
    client.generate(text="...", voice="adam_rocha")
except Exception as e:
    print(e)  # "Text must contain at least one alphanumeric character"
```

### Recomendações por Tamanho

| Tamanho do Texto | Método Recomendado | Observações |
|------------------|-------------------|-------------|
| < 500 chars | `generate()` ou `generate_stream()` | Síntese simples via HTTP |
| 500 - 1k chars | `generate_stream()` ou `stream_text()` | HTTP streaming funciona bem |
| 1k - 10k chars | `stream_text()` ou sessão persistente | **WebSocket OBRIGATÓRIO para textos longos** |
| 10k - 50k chars | Sessão persistente com múltiplas mensagens | Dividir em parágrafos via WebSocket |
| > 50k chars | Dividir em múltiplas requisições | Múltiplas sínteses necessárias |

⚠️ **IMPORTANTE**: O endpoint HTTP `generate_stream()` tem limitações com textos longos e pode processar apenas a primeira sentença. Para textos > 1000 caracteres, **sempre use WebSocket** (`stream_text()` ou sessões persistentes).

**Dica**: Para textos grandes (> 10k), divida em parágrafos e envie múltiplas mensagens via WebSocket para melhor experiência.

### Funcionalidades de Normalização

A API normaliza automaticamente:

- 💰 **Moedas**: `R$ 99,90` → "noventa e nove reais e noventa centavos"
- 💵 **Dólares**: `$49.99` → "quarenta e nove dólares e noventa e nove centavos"
- 📏 **Espaços**: Remove espaços duplicados
- 📝 **Pontuação**: Normaliza reticências e pontos

```python
# Exemplo com moedas
audio = client.generate(
    text="O produto custa R$ 150,00 e o frete é US$ 25,50",
    voice="adam_rocha"
)
# TTS irá falar: "O produto custa cento e cinquenta reais e o frete é vinte e cinco dólares e cinquenta centavos"
```

## Configuração

### Base URL

- **Produção**: `https://api.talklabs.com.br`
- **Local**: `http://localhost:5000` (desenvolvimento)

### Endpoints

- **HTTP**: `/v1/text-to-speech/{voice_id}`
- **WebSocket**: `/v1/text-to-speech/{voice_id}/stream`

## Troubleshooting

### Erro: "Connection refused"

Verifique se a API está rodando:
```bash
curl https://api.talklabs.com.br/health
```

### Latência alta no streaming

1. Use `stream_text()` ou sessão persistente ao invés de `generate_stream()`
2. Verifique sua conexão com a API
3. Certifique-se que está usando a região mais próxima

### Chunks de áudio corrompidos

- Certifique-se de salvar/reproduzir como WAV 24kHz mono
- Use `io.BytesIO` para buffer temporário se necessário

---

## 🆘 Suporte

- 📧 **Email**: support@talklabs.com.br
- 🌐 **Website**: https://talklabs.com.br
- 💡 **Exemplos**: Ver pasta `examples/` incluída no pacote
- 📚 **Documentação**: Ver seção API Reference acima

---

## 📄 Licença

MIT License - veja LICENSE para detalhes.

---

**Desenvolvido com ❤️ pela equipe TalkLabs**
