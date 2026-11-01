"""Monitora janelas ativas e registra o tempo de uso em um arquivo CSV."""

import csv
import time
from ctypes import create_unicode_buffer
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import keyboard
import pyautogui
from plyer import notification


NOME_APLICACAO = "Monitor de Atividade"
TECLA_PAUSA = "ctrl + k"
LIMITE_INATIVIDADE_SEGUNDOS = 120


class MonitorDeAtividade:
    """Monitora a janela ativa, a atividade do mouse e grava os registros."""

    def __init__(self) -> None:
        """Inicializa o estado do monitor e define o arquivo CSV do dia."""
        data_atual = datetime.now().date().isoformat()
        self.caminho_log = Path.cwd() / "log" / f"logger_{data_atual}.csv"
        agora = datetime.now()
        self.janela_atual = ""
        self.inicio_janela_atual = agora
        self.posicao_mouse = pyautogui.position()
        self.ultima_atividade_mouse = agora
        self.inatividade_registrada = False

    def obter_titulo_janela_ativa(self) -> Optional[str]:
        """Retorna o título da janela em primeiro plano ou ``None``."""
        from ctypes import windll

        identificador = windll.user32.GetForegroundWindow()
        if not identificador:
            return None

        tamanho = windll.user32.GetWindowTextLengthW(identificador)
        buffer = create_unicode_buffer(tamanho + 1)
        windll.user32.GetWindowTextW(identificador, buffer, tamanho + 1)
        return buffer.value or None

    def gravar_registro(self, titulo: str, duracao: timedelta) -> None:
        """Acrescenta ao CSV a data, o título da janela e a duração."""
        self.caminho_log.parent.mkdir(parents=True, exist_ok=True)
        horario = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        titulo = titulo.replace("\\u25cf", "")

        with self.caminho_log.open("a", newline="", encoding="utf-8") as arquivo:
            escritor = csv.writer(arquivo, delimiter=";")
            escritor.writerow([horario, titulo, str(duracao)])

    def registrar_troca_de_janela(self, novo_titulo: str) -> None:
        """Registra a janela anterior e inicia a contagem da nova janela."""
        agora = datetime.now()
        if self.janela_atual:
            duracao = agora - self.inicio_janela_atual
            self.gravar_registro(self.janela_atual, duracao)

        self.janela_atual = novo_titulo
        self.inicio_janela_atual = agora
        self.posicao_mouse = pyautogui.position()
        self.ultima_atividade_mouse = agora
        self.inatividade_registrada = False

    def verificar_inatividade(self) -> None:
        """Registra uma ocorrência quando o mouse fica parado por dois minutos."""
        agora = datetime.now()
        posicao_atual = pyautogui.position()

        if posicao_atual != self.posicao_mouse:
            self.posicao_mouse = posicao_atual
            self.ultima_atividade_mouse = agora
            self.inatividade_registrada = False
            return

        duracao = agora - self.ultima_atividade_mouse
        if (
            duracao.total_seconds() >= LIMITE_INATIVIDADE_SEGUNDOS
            and not self.inatividade_registrada
        ):
            self.gravar_registro("possivel ausencia temporaria > 2min", duracao)
            self.inatividade_registrada = True

    def pausar(self) -> None:
        """Pausa a execução até que o usuário pressione Enter."""
        input("Pressione <ENTER> para continuar...")

    def executar(self) -> None:
        """Inicia o aviso e executa o monitor até o usuário interrompê-lo."""
        notification.notify(
            title="Monitor de Atividade Iniciado",
            message=(
                "Durante o monitoramento, pressione <CTRL + K> para pausar "
                "ou <CTRL + C> para encerrar."
            ),
            app_name=NOME_APLICACAO,
            timeout=20,
        )

        try:
            while True:
                if keyboard.is_pressed(TECLA_PAUSA):
                    self.pausar()

                titulo = self.obter_titulo_janela_ativa()
                if titulo and titulo != self.janela_atual:
                    self.registrar_troca_de_janela(titulo)
                else:
                    self.verificar_inatividade()

                time.sleep(1)
        finally:
            if self.janela_atual:
                duracao = datetime.now() - self.inicio_janela_atual
                self.gravar_registro(self.janela_atual, duracao)


def iniciar_monitoramento() -> None:
    """Cria o monitor e inicia a coleta de atividade."""
    MonitorDeAtividade().executar()
