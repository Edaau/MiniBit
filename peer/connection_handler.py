import threading
import socket
import json
import os
from file.block import Block
from tit_for_tat import TitForTatManager

class ConnectionHandler:
    def __init__(self, peerId, ip, port, blocos, pasta):
        self.peerId = peerId
        self.ip = ip
        self.port = port
        self.blocos = blocos  # conjunto de blocos disponíveis
        self.pasta = pasta  # diretório onde os blocos estão salvos
        self.lock = threading.Lock()
        self.titForTat = TitForTatManager()  # controle de upload

    def iniciarServidor(self):
        thread = threading.Thread(target=self.escutarPeers)
        thread.start()

    def escutarPeers(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((self.ip, self.port))
                s.listen()
                print(f"[{self.peerId}] Servidor escutando em {self.ip}:{self.port}")

                while True:
                    conn, addr = s.accept()
                    thread = threading.Thread(target=self.tratarConexao, args=(conn,))
                    thread.start()
        except Exception as e:
            print(f"[{self.peerId}] Erro no servidor: {e}")

    def tratarConexao(self, conn):
        try:
            with conn:
                data = conn.recv(1024)
                if not data:
                    return

                pedido = json.loads(data.decode())
                blocoId = pedido.get("bloco")
                peerRemoto = pedido.get("peerId")

                if blocoId is None or peerRemoto is None:
                    return

                if not self.titForTat.estaDesbloqueado(peerRemoto):
                    print(f"[{self.peerId}] Peer {peerRemoto} bloqueado (Tit-for-Tat)")
                    return

                if blocoId in self.blocos:
                    bloco = self.lerBloco(blocoId)
                    resposta = bloco.getDict()
                    conn.sendall(json.dumps(resposta).encode())
                    self.titForTat.atualizarUpload(peerRemoto)
                    print(f"[{self.peerId}] Enviou bloco {blocoId} para {peerRemoto}")
        except Exception as e:
            print(f"[{self.peerId}] Erro ao tratar conexao: {e}")

    def lerBloco(self, blocoId):
        try:
            caminho = os.path.join(self.pasta, f"block_{blocoId}")
            with open(caminho, "rb") as f:
                dados = f.read()
                return Block(blocoId, dados)
        except:
            return Block(blocoId, b"DADOS_FAKE")