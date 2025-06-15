import socket
import threading
import json
import random
import sys
import os
import math
from tracker.PeerInfo import PeerInfo
from peer.Peer import Peer  
from file.file_manager import FileManager  

BLOCO_TAMANHO = 256 * 1024  # 256 KB
BLOCOS_POR_PEER = 4         # Blocos aleatorios que cada peer recebe
PASTA_BLOCOS_ORIGINAIS = "blocos_originais"

class Tracker:
    def __init__(self, host, port, arquivoPath):
        self.host = host
        self.port = port
        self.peers = []
        self.lock = threading.Lock()

        # Divide o arquivo original em blocos reais
        FileManager(arquivoPath, PASTA_BLOCOS_ORIGINAIS).splitFile()

        # Calcula numero total de blocos baseado no arquivo
        if not os.path.exists(arquivoPath):
            raise FileNotFoundError(f"Arquivo nao encontrado: {arquivoPath}")

        tamanhoArquivo = os.path.getsize(arquivoPath)
        self.totalBlocos = math.ceil(tamanhoArquivo / BLOCO_TAMANHO)
        print(f"[TRACKER] Arquivo: {arquivoPath} ({tamanhoArquivo} bytes)")
        print(f"[TRACKER] Bloco: {BLOCO_TAMANHO} bytes")
        print(f"[TRACKER] Total de blocos calculado: {self.totalBlocos}")

    def start(self):
        print(f"[TRACKER] Iniciando servidor em {self.host}:{self.port}")

        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind((self.host, self.port))
            server_socket.listen()
            print("[TRACKER] Esperando conexoes de peers...")

            while True:
                try:
                    conn, addr = server_socket.accept()
                    print(f"[TRACKER] Conexao recebida de {addr}")
                    thread = threading.Thread(target=self.handlePeer, args=(conn,))
                    thread.start()
                except Exception as e:
                    print(f"[TRACKER] Erro ao aceitar conexao: {e}")
        except Exception as e:
            print(f"[TRACKER] Erro ao iniciar servidor: {e}")

    def handlePeer(self, conn):
        try:
            with conn:
                data = conn.recv(4096)

                if not data:
                    print("[TRACKER] Dados vazios recebidos.")
                    return

                try:
                    peerDict = json.loads(data.decode())
                except Exception as e:
                    print(f"[TRACKER] Erro ao decodificar JSON: {e}")
                    return

                # Se for o tracker se registrando como peer, vira seeder
                if peerDict.get("id") == "tracker":
                    blocosAleatorios = list(range(self.totalBlocos))
                    print(f"[TRACKER] Atuando como peer seeder com todos os blocos.")
                else:
                    blocosAleatorios = random.sample(
                        range(self.totalBlocos),
                        min(BLOCOS_POR_PEER, self.totalBlocos)
                    )

                peerDict["blocks"] = blocosAleatorios
                peer = PeerInfo.setDict(peerDict)

                with self.lock:
                    self.registrarOuAtualizarPeer(peer)
                    resposta = [p.getDict() for p in self.peers] 

                conn.sendall(json.dumps(resposta).encode())
                print(f"[TRACKER] Peer {peer.id} registrado com blocos: {blocosAleatorios}")
        except Exception as e:
            print(f"[TRACKER] Erro ao lidar com peer: {e}")

    def registrarOuAtualizarPeer(self, novoPeer):
        for i, peer in enumerate(self.peers):
            if peer.id == novoPeer.id:
                self.peers[i] = novoPeer
                print(f"[TRACKER] Peer {novoPeer.id} atualizado.")
                return
        self.peers.append(novoPeer)
        print(f"[TRACKER] Peer {novoPeer.id} adicionado.")

# Execucao: python Tracker.py <IP> <PORTA> <CAMINHO_ARQUIVO>
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Uso: python tracker.py <IP> <PORTA> <CAMINHO_ARQUIVO>")
        sys.exit(1)

    ip = sys.argv[1]
    try:
        porta = int(sys.argv[2])
    except ValueError:
        print("A porta deve ser um numero inteiro.")
        sys.exit(1)

    caminhoArquivo = sys.argv[3]

    try:
        # Inicia o Tracker
        tracker = Tracker(ip, porta, caminhoArquivo)
        trackerThread = threading.Thread(target=tracker.start, daemon=True)
        trackerThread.start()

        # Inicia o Peer Seeder no mesmo processo
        print("[TRACKER] Iniciando peer local com ID 'tracker' como seeder...")
        peerSeeder = Peer("tracker", ip, 9001, ip, porta)
        peerSeeder.start()

    except Exception as e:
        print(f"[ERRO] {e}")
