"""
TalkLabs Python SDK v2.1.5
---------------------------
SDK minimalista para TTS streaming com sessões persistentes.

Instalação:
    pip install talklabs

Uso:
    from talklabs import TalkLabsClient

    # One-shot (síntese única)
    client = TalkLabsClient(api_key="tlk_live_xxxxx")
    async for chunk in client.stream_text("Olá!", voice="adam_rocha"):
        play(chunk)

    # Persistente (múltiplas sínteses)
    session = await client.create_session(voice="adam_rocha")
    async for chunk in session.stream_text("Frase 1"):
        play(chunk)
    async for chunk in session.stream_text("Frase 2"):
        play(chunk)
    await session.close()
"""

import json
import logging
from typing import Optional, AsyncIterator
from dataclasses import dataclass
import websockets

# ============================================================
# LOGGING
# ============================================================

logger = logging.getLogger("talklabs")
logger.setLevel(logging.INFO)

if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter("[%(levelname)s] %(name)s: %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)


# ============================================================
# CLASSE: VoiceSettings (Opcional)
# ============================================================

@dataclass
class VoiceSettings:
    """
    Configurações opcionais de voz.

    Args:
        stability: Estabilidade da voz (0.0-1.0, padrão: 0.75)
        similarity_boost: Aumento de similaridade (0.0-1.0, padrão: 0.75)
        style: Estilo da fala (0.0-1.0, padrão: 0.0)
        use_speaker_boost: Aumentar clareza do falante (padrão: True)
    """
    stability: float = 0.75
    similarity_boost: float = 0.75
    style: float = 0.0
    use_speaker_boost: bool = True

    def to_dict(self):
        """Converte para dict para envio via API."""
        return {
            "stability": self.stability,
            "similarity_boost": self.similarity_boost,
            "style": self.style,
            "use_speaker_boost": self.use_speaker_boost,
        }


# ============================================================
# CLASSE: StreamingSession (Sessão Persistente)
# ============================================================

class StreamingSession:
    """
    Sessão persistente de streaming que mantém a conexão WebSocket aberta
    para processar múltiplas frases sem reconectar.

    Uso:
        session = await client.create_session(voice="adam_rocha")

        async for chunk in session.stream_text("Frase 1"):
            play(chunk)

        async for chunk in session.stream_text("Frase 2"):
            play(chunk)

        await session.close()
    """

    def __init__(self, websocket, voice: str, language: str = "pt",
                 speed: float = 1.0, voice_settings: Optional[VoiceSettings] = None):
        self.ws = websocket
        self.voice = voice
        self.language = language
        self.speed = speed
        self.voice_settings = voice_settings
        self._is_closed = False

    async def stream_text(self, text: str) -> AsyncIterator[bytes]:
        """
        Processa uma frase e retorna os chunks de áudio.
        A sessão permanece aberta para processar mais frases depois.

        Args:
            text: Texto da frase a ser sintetizada

        Yields:
            bytes: Chunks de áudio WAV
        """
        if self._is_closed:
            raise RuntimeError("Sessão já foi encerrada")

        logger.info("[Session] Processando frase: %s...", text[:50])

        # Envia o texto
        logger.info("[Session] Enviando texto para servidor...")
        await self.ws.send(json.dumps({"text": text}))
        logger.info("[Session] Texto enviado!")

        # Envia flush parcial (finaliza apenas esta frase)
        logger.info("[Session] Enviando flush_partial...")
        await self.ws.send(json.dumps({"flush_partial": True}))
        logger.info("[Session] flush_partial enviado! Aguardando respostas...")

        chunk_count = 0
        # Aguarda chunks até receber confirmação de flush parcial
        while True:
            logger.debug("[Session] Aguardando próxima mensagem do servidor...")
            message = await self.ws.recv()
            msg_size = len(message) if isinstance(message, bytes) else 'N/A'
            logger.debug("[Session] Mensagem recebida: tipo=%s, tamanho=%s",
                        type(message), msg_size)

            # Mensagem binária (áudio)
            if isinstance(message, bytes):
                chunk_count += 1
                logger.info("[Session] Chunk %d de áudio recebido (%d bytes)",
                           chunk_count, len(message))
                yield message
                continue

            # Mensagem JSON (eventos)
            try:
                data = json.loads(message)
                logger.info("[Session] Evento recebido: %s", data)
            except json.JSONDecodeError:
                logger.warning("[Session] Mensagem não é JSON válido")
                continue

            # Eventos
            if data.get("event") == "partial_flush_complete":
                logger.info("[Session] Frase finalizada! Total: %d chunks de áudio",
                           chunk_count)
                break
            if data.get("event") == "end_of_stream":
                logger.info("[Session] Stream encerrado pelo servidor. Total: %d chunks",
                           chunk_count)
                self._is_closed = True
                break
            if data.get("event") == "error":
                error_msg = data.get("message", "Erro desconhecido")
                logger.error("[Session] Erro: %s", error_msg)
                raise Exception(f"Session error: {error_msg}")

    async def close(self):
        """Encerra a sessão e fecha a conexão WebSocket."""
        if not self._is_closed:
            try:
                await self.ws.close()
                self._is_closed = True
                logger.info("[Session] Sessão encerrada")
            except Exception as ex:
                logger.warning("[Session] Erro ao fechar: %s", ex)

    # Context manager support (opcional - compatibilidade)
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# ============================================================
# CLASSE PRINCIPAL: TalkLabsClient
# ============================================================

class TalkLabsClient:
    """
    Cliente TalkLabs para síntese de voz com streaming Redis.

    Features:
        - Streaming ultra-low latency (~200-500ms)
        - Sessões persistentes (reutilização de conexão)
        - Keep-alive automático (ping/pong)
        - API unificada (stream_text)

    Args:
        api_key: Chave de API TalkLabs (ex: "tlk_live_xxxxx")
        base_url: URL base da API (padrão: "https://api.talklabs.com.br")
        timeout: Timeout para requisições (padrão: 60s)

    Example:
        >>> client = TalkLabsClient(api_key="tlk_live_xxxxx")
        >>>
        >>> # One-shot (síntese única)
        >>> async for chunk in client.stream_text("Olá!", voice="adam_rocha"):
        ...     play_audio(chunk)
        >>>
        >>> # Persistente (múltiplas sínteses)
        >>> session = await client.create_session(voice="adam_rocha")
        >>> async for chunk in session.stream_text("Frase 1"):
        ...     play_audio(chunk)
        >>> async for chunk in session.stream_text("Frase 2"):
        ...     play_audio(chunk)
        >>> await session.close()
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.talklabs.com.br",
        timeout: int = 60
    ):
        """
        Inicializa o cliente TalkLabs.

        Args:
            api_key: Chave de API TalkLabs (ex: "tlk_live_xxxxx")
            base_url: URL base da API
            timeout: Tempo máximo de espera (em segundos)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        logger.info("TalkLabsClient inicializado com base_url=%s", self.base_url)

    # ============================================================
    # MÉTODO: create_session() - Cria sessão persistente
    # ============================================================

    async def create_session(
        self,
        voice: str,
        language: str = "pt",
        speed: float = 1.0,
        voice_settings: Optional[VoiceSettings] = None,
        ping_interval: float = 20.0,
        ping_timeout: float = 20.0,
    ) -> StreamingSession:
        """
        Cria uma sessão persistente de streaming que mantém a conexão WebSocket
        aberta para processar múltiplas frases sem reconectar.

        A sessão permanece ativa indefinidamente até que:
        - close() seja chamado explicitamente
        - Timeout de inatividade (ping/pong falhar)
        - Erro de conexão

        Args:
            voice: ID da voz TalkLabs (ex: "adam_rocha", "adam_rocha")
            language: Código do idioma ("pt", "en", etc)
            speed: Velocidade de reprodução (0.5-2.0)
            voice_settings: Configurações opcionais de voz
            ping_interval: Intervalo entre pings (segundos, padrão: 20)
            ping_timeout: Timeout para pong (segundos, padrão: 20)

        Returns:
            StreamingSession: Objeto de sessão que pode processar múltiplas frases

        Example:
            >>> client = TalkLabsClient(api_key="tlk_live_xxxxx")
            >>> session = await client.create_session(voice="adam_rocha")
            >>>
            >>> # Primeira frase
            >>> async for chunk in session.stream_text("Olá, como vai?"):
            ...     play_audio(chunk)
            >>>
            >>> # Segunda frase (mesma conexão!)
            >>> async for chunk in session.stream_text("Tudo bem?"):
            ...     play_audio(chunk)
            >>>
            >>> # Fecha quando terminar
            >>> await session.close()
        """
        # Conecta ao endpoint de streaming Redis
        base = self.base_url.replace('https', 'wss').replace('http', 'ws')
        ws_url = f"{base}/v1/text-to-speech/{voice}/stream-redis"

        logger.info("[TalkLabs] Criando sessão persistente: %s", ws_url)

        try:
            # Conecta ao WebSocket com keep-alive configurável
            ws = await websockets.connect(
                ws_url,
                ping_interval=ping_interval,
                ping_timeout=ping_timeout
            )
            logger.info("[TalkLabs] Sessão conectada! (ping=%ss, timeout=%ss)",
                       ping_interval, ping_timeout)

            # 1. Autenticação
            auth_payload = {"xi_api_key": self.api_key}
            await ws.send(json.dumps(auth_payload))
            logger.debug("[TalkLabs] Autenticação enviada")

            # Cria e retorna a sessão
            session = StreamingSession(
                websocket=ws,
                voice=voice,
                language=language,
                speed=speed,
                voice_settings=voice_settings
            )

            logger.info("[TalkLabs] Sessão pronta para uso!")
            return session

        except Exception as ex:
            logger.exception("[TalkLabs] Erro ao criar sessão: %s", ex)
            raise ex

    # ============================================================
    # MÉTODO: stream_text() - Streaming one-shot (sem persistência)
    # ============================================================

    async def stream_text(
        self,
        text: str,
        voice: str,
        language: str = "pt",
        speed: float = 1.0,
        voice_settings: Optional[VoiceSettings] = None,
    ) -> AsyncIterator[bytes]:
        """
        Sintetiza texto usando streaming Redis SEM sessão persistente.

        Este método cria uma nova conexão WebSocket, sintetiza o texto,
        e fecha a conexão automaticamente. Ideal para sínteses únicas.

        Para múltiplas sínteses, use create_session() + session.stream_text()
        para reutilizar a mesma conexão e reduzir latência.

        Args:
            text: Texto para sintetizar
            voice: ID da voz (ex: "adam_rocha")
            language: Código do idioma (padrão: "pt")
            speed: Velocidade de reprodução (0.5-2.0)
            voice_settings: Configurações opcionais de voz

        Yields:
            bytes: Chunks de áudio WAV

        Example (One-shot - sem persistência):
            >>> client = TalkLabsClient(api_key="tlk_live_xxxxx")
            >>> async for chunk in client.stream_text("Olá!", voice="adam_rocha"):
            ...     play_audio(chunk)

        Example (Persistente - múltiplas sínteses):
            >>> session = await client.create_session(voice="adam_rocha")
            >>> async for chunk in session.stream_text("Frase 1"):
            ...     play_audio(chunk)
            >>> async for chunk in session.stream_text("Frase 2"):
            ...     play_audio(chunk)
        """
        logger.info("[TalkLabs] stream_text() one-shot: %s...", text[:50])

        # Cria sessão temporária
        session = await self.create_session(
            voice=voice,
            language=language,
            speed=speed,
            voice_settings=voice_settings,
            ping_interval=20.0,
            ping_timeout=20.0
        )

        try:
            # Sintetiza usando a sessão temporária
            async for chunk in session.stream_text(text):
                yield chunk
        finally:
            # Sempre fecha a sessão temporária
            await session.close()
            logger.debug("[TalkLabs] Sessão temporária encerrada")

    # ============================================================
    # MÉTODOS UTILITÁRIOS (para testes e uso simples)
    # ============================================================

    def generate(
        self,
        text: str,
        voice: str,
        language: str = "pt",
        speed: float = 1.0,
        voice_settings: Optional[VoiceSettings] = None,
    ) -> bytes:
        """
        Gera áudio completo (síncrono) via HTTP.

        Método utilitário para testes simples. Para produção,
        use stream_text() para melhor latência.

        Args:
            text: Texto para sintetizar
            voice: ID da voz (ex: "adam_rocha")
            language: Código do idioma (padrão: "pt")
            speed: Velocidade de reprodução (0.5-2.0)
            voice_settings: Configurações opcionais de voz

        Returns:
            bytes: Áudio completo em formato WAV

        Example:
            >>> client = TalkLabsClient(api_key="tlk_live_xxxxx")
            >>> audio = client.generate("Olá!", voice="adam_rocha")
            >>> with open("output.wav", "wb") as f:
            ...     f.write(audio)
        """
        import requests

        url = f"{self.base_url}/v1/text-to-speech/{voice}"
        payload = {
            "text": text,
            "language_code": language,
            "speed": speed
        }

        if voice_settings:
            payload["voice_settings"] = voice_settings.to_dict()

        logger.info("[TalkLabs] Gerando áudio síncrono: %s...", text[:50])

        try:
            response = requests.post(
                url,
                headers={"xi-api-key": self.api_key},
                json=payload,
                timeout=self.timeout
            )

            if response.status_code != 200:
                logger.error("Erro %d: %s", response.status_code, response.text)
                raise Exception(f"API Error: {response.status_code} - {response.text}")

            logger.info("Áudio gerado com sucesso")
            return response.content

        except Exception as ex:
            logger.exception("Erro ao gerar áudio: %s", ex)
            raise ex

    def generate_stream(
        self,
        text: str,
        voice: str,
        language: str = "pt",
        speed: float = 1.0,
        voice_settings: Optional[VoiceSettings] = None,
    ):
        """
        Gera áudio em chunks via HTTP streaming.

        Método utilitário para testes. Para produção, use stream_text()
        que usa WebSocket e tem menor latência.

        Args:
            text: Texto para sintetizar
            voice: ID da voz
            language: Código do idioma
            speed: Velocidade de reprodução
            voice_settings: Configurações opcionais

        Yields:
            bytes: Chunks de áudio progressivamente

        Example:
            >>> client = TalkLabsClient(api_key="tlk_live_xxxxx")
            >>> for chunk in client.generate_stream("Olá!", voice="adam_rocha"):
            ...     play_audio(chunk)
        """
        import requests

        url = f"{self.base_url}/v1/text-to-speech/{voice}/stream"
        payload = {
            "text": text,
            "language_code": language,
            "speed": speed
        }

        if voice_settings:
            payload["voice_settings"] = voice_settings.to_dict()

        logger.info("[TalkLabs] Streaming HTTP: %s...", text[:50])

        try:
            with requests.post(
                url,
                headers={"xi-api-key": self.api_key},
                json=payload,
                stream=True,
                timeout=self.timeout
            ) as response:

                if response.status_code != 200:
                    logger.error("Erro %d", response.status_code)
                    raise Exception(f"API Error: {response.status_code}")

                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        yield chunk

            logger.info("Streaming HTTP finalizado")

        except Exception as ex:
            logger.exception("Erro durante streaming HTTP: %s", ex)
            raise ex

    def get_voices(self):
        """
        Lista todas as vozes disponíveis.

        Método utilitário para exploração da API.

        Returns:
            list: Lista de vozes disponíveis

        Example:
            >>> client = TalkLabsClient(api_key="tlk_live_xxxxx")
            >>> voices = client.get_voices()
            >>> for voice in voices:
            ...     print(f"{voice['voice_id']}: {voice['name']}")
        """
        import requests

        url = f"{self.base_url}/v1/voices"

        try:
            response = requests.get(
                url,
                headers={"xi-api-key": self.api_key},
                timeout=self.timeout
            )

            if response.status_code != 200:
                logger.error("Erro %d: %s", response.status_code, response.text)
                raise Exception(f"API Error: {response.status_code}")

            data = response.json()
            return data.get("voices", [])

        except Exception as ex:
            logger.exception("Erro ao buscar vozes: %s", ex)
            raise ex
