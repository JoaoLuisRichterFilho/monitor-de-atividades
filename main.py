"""Ponto de entrada do monitor de atividade."""

from src.PythonLogger import iniciar_monitoramento


if __name__ == "__main__":
    try:
        iniciar_monitoramento()
    except KeyboardInterrupt:
        print("Monitoramento encerrado.")
