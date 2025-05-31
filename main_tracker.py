from tracker.Tracker import Tracker

if __name__ == "__main__":
    # Parametros fixos para facilitar a execucao
    ip = "192.168.0.62"
    porta = 8000
    caminhoArquivo = "D:\\livro_vitima.pdf"

    try:
        print(f"[MAIN] Iniciando Tracker em {ip}:{porta} usando arquivo '{caminhoArquivo}'")
        tracker = Tracker(ip, porta, caminhoArquivo)
        tracker.start()
    except Exception as e:
        print(f"[MAIN] Erro ao iniciar o Tracker: {e}")