import socket
import threading
import json
import sys
import time
import os
from tracker.PeerInfo import PeerInfo

PASTA_BLOCOS = "blocos_recebidos"

class Peer:
    def init(self, peerId, ip, port, trackerIp, trackerPort):
        self.id = peerId
        self.ip = ip
        self.port = port
        self.trackerIp = trackerIp
        self.trackerPort = trackerPort
        self.listaPeers = []
        self.blocos = set()
        self.totalBlocos = None
        self.lock = threading.Lock()

    if not os.path.exists(PASTA_BLOCOS):
        os.makedirs(PASTA_BLOCOS)

    def start(self):
        print(f"[{self.id}] Iniciando peer em {self.ip}:{self.port}")
        self.registrarNoTracker()

        #inicia a thread para escutar outros peers
        threadServidor = threading.Thread(target=self.escutarOutrosPeers)
        threadServidor.start()

        #tenta se conectar a outros peers
        self.conectarAosPeers()

        #loop principal de requisição
        while not self.possuiTodosBlocos():
            self.requisitarBlocosFaltantes()
            time.sleep(5)

        print(f"[{self.id}] Arquivo completo! Todos os blocos foram recebidos.")

    def registrarNoTracker(self):
        peerDict = {
            "id": self.id,
            "ip": self.ip,
            "port": self.port,
            "blocks": []
        }

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.trackerIp, self.trackerPort))
                s.sendall(json.dumps(peerDict).encode())
                resposta = s.recv(4096)
                lista = json.loads(resposta.decode())

                self.listaPeers = lista
                print(f"[{self.id}] Tracker retornou {len(lista)} peer(s).")

                #recupera os blocos escolhidos
                blocosAtribuidos = peerDict.get("blocks", [])
                self.blocos.update(blocosAtribuidos)
                for bloco in blocosAtribuidos:
                    self.salvarBloco(bloco)

        except Exception as e:
            print(f"[{self.id}] Erro ao conectar no tracker: {e}")

    def escutarOutrosPeers(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                server_socket.bind((self.ip, self.port))
                server_socket.listen()

                print(f"[{self.id}] Esperando conexoes de outros peers...")

                while True:
                    conn, addr = server_socket.accept()
                    thread = threading.Thread(target=self.lidarComPeer, args=(conn,))
                    thread.start()

        except Exception as e:
            print(f"[{self.id}] Erro no servidor peer: {e}")

    def lidarComPeer(self, conn):
        try:
            with conn:
                data = conn.recv(1024)
                if not data:
                    return

                pedido = json.loads(data.decode())
                blocoSolicitado = pedido.get("bloco")
                print(f"[{self.id}] Recebeu pedido de bloco {blocoSolicitado}")

                if blocoSolicitado in self.blocos:
                    conteudo = self.lerBloco(blocoSolicitado)
                    resposta = {
                        "bloco": blocoSolicitado,
                        "dados": conteudo
                    }
                    conn.sendall(json.dumps(resposta).encode())
        except Exception as e:
            print(f"[{self.id}] Erro ao lidar com outro peer: {e}")

    def conectarAosPeers(self):
        for peer in self.listaPeers:
            peerId = peer["id"]
            peerIp = peer["ip"]
            peerPort = peer["port"]
            print(f"[{self.id}] Pode tentar se conectar a {peerId} em {peerIp}:{peerPort}")

    def requisitarBlocosFaltantes(self):
        blocosNecessarios = self.obterBlocosFaltantes()
        if not blocosNecessarios:
            return

        for bloco in blocosNecessarios:
            for peer in self.listaPeers:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(2)
                        s.connect((peer["ip"], peer["port"]))
                        pedido = {"bloco": bloco}
                        s.sendall(json.dumps(pedido).encode())

                        resposta = s.recv(4096)
                        dados = json.loads(resposta.decode())
                        if dados.get("bloco") == bloco:
                            self.salvarBloco(bloco, dados.get("dados"))
                            with self.lock:
                                self.blocos.add(bloco)
                            print(f"[{self.id}] Recebeu bloco {bloco} de {peer['id']}")
                            break  #vai para o proximo bloco

                except Exception:
                    continue  #tenta executar com o proximo peer

    def salvarBloco(self, blocoId, conteudo="DADOS_FAKE"):
        nomeArquivo = os.path.join(PASTA_BLOCOS, f"block_{blocoId}")
        try:
            with open(nomeArquivo, "w") as f:
                f.write(conteudo)
        except Exception as e:
            print(f"[{self.id}] Erro ao salvar bloco {blocoId}: {e}")

    def lerBloco(self, blocoId):
        nomeArquivo = os.path.join(PASTA_BLOCOS, f"block_{blocoId}")
        try:
            with open(nomeArquivo, "r") as f:
                return f.read()
        except Exception:
            return "DADOS_FAKE"

    def obterBlocosFaltantes(self):
        if self.totalBlocos is None:
            self.totalBlocos = self.detectarTotalBlocos()

        return [i for i in range(self.totalBlocos) if i not in self.blocos]

    def detectarTotalBlocos(self):
        arquivos = os.listdir(PASTA_BLOCOS)
        if not arquivos:
            return 10  #valor default
        numeros = [int(a.split("_")[1]) for a in arquivos if a.startswith("block_")]
        return max(numeros) + 1

    def possuiTodosBlocos(self):
        return len(self.blocos) == self.totalBlocos
