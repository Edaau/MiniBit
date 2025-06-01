import socket
import threading
import json
import time
import os
from tracker.PeerInfo import PeerInfo
from file.block import Block
from strategies.rarest_first import RarestFirst
from tit_for_tat import TitForTatManager

PASTA_BLOCOS = "blocos_recebidos"

class Peer:
    def __init__(self, peerId, ip, port, trackerIp, trackerPort):
        self.id = peerId
        self.ip = ip
        self.port = port
        self.trackerIp = trackerIp
        self.trackerPort = trackerPort
        self.listaPeers = []
        self.blocos = set()
        self.totalBlocos = None
        self.lock = threading.Lock()
        self.rarest = RarestFirst()
        self.titForTat = TitForTatManager()

        if not os.path.exists(PASTA_BLOCOS):
            os.makedirs(PASTA_BLOCOS)

    def start(self):
        print(f"[{self.id}] Iniciando peer em {self.ip}:{self.port}")
        self.registrarNoTracker()

        threadServidor = threading.Thread(target=self.escutarOutrosPeers)
        threadServidor.start()

        while not self.possuiTodosBlocos():
            self.requisitarBlocoMaisRaro()
            time.sleep(5)

        print(f"[{self.id}] Arquivo completo! Todos os blocos foram recebidos.")

    def registrarNoTracker(self):
        meuPeer = PeerInfo(self.id, self.ip, self.port, [])
        peerDict = meuPeer.getDict()

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.trackerIp, self.trackerPort))
                s.sendall(json.dumps(peerDict).encode())
                resposta = s.recv(4096)
                lista = json.loads(resposta.decode())

                self.listaPeers = lista
                print(f"[{self.id}] Tracker retornou {len(lista)} peer(s).")

                blocosAtribuidos = [p["blocks"] for p in lista if p["id"] == self.id]
                if blocosAtribuidos:
                    for bloco in blocosAtribuidos[0]:
                        fakeData = f"Conteudo do bloco {bloco}".encode("utf-8")
                        self.salvarBloco(Block(bloco, fakeData))
                        self.blocos.add(bloco)

                todosBlocos = []
                for p in lista:
                    self.rarest.updatePeerBlocks(p["id"], p["blocks"])
                    todosBlocos.extend(p["blocks"])
                self.totalBlocos = max(todosBlocos) + 1 if todosBlocos else 10

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
                    thread = threading.Thread(target=self.lidarComPeer, args=(conn, addr))
                    thread.start()

        except Exception as e:
            print(f"[{self.id}] Erro no servidor peer: {e}")

    def lidarComPeer(self, conn, addr):
        try:
            peerIp, _ = addr
            with conn:
                data = conn.recv(1024)
                if not data:
                    return

                pedido = json.loads(data.decode())
                blocoSolicitado = pedido.get("bloco")
                peerIdRemoto = pedido.get("peerId")

                print(f"[{self.id}] Pedido de bloco {blocoSolicitado} de {peerIdRemoto}")

                if not self.titForTat.estaDesbloqueado(peerIdRemoto):
                    print(f"[{self.id}] Peer {peerIdRemoto} bloqueado (Tit-for-Tat)")
                    return

                if blocoSolicitado in self.blocos:
                    bloco = self.lerBloco(blocoSolicitado)
                    resposta = bloco.getDict()
                    conn.sendall(json.dumps(resposta).encode())
                    self.titForTat.atualizarUpload(peerIdRemoto)
        except Exception as e:
            print(f"[{self.id}] Erro ao lidar com peer: {e}")

    def requisitarBlocoMaisRaro(self):
        bloco = self.rarest.escolherBlocoRaro(self.blocos)
        if bloco is None:
            return

        for peer in self.listaPeers:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(2)
                    s.connect((peer["ip"], peer["port"]))
                    pedido = {"bloco": bloco, "peerId": self.id}
                    s.sendall(json.dumps(pedido).encode())

                    resposta = s.recv(4096)
                    dados = json.loads(resposta.decode())
                    blocoObj = Block.setDict(dados)

                    self.salvarBloco(blocoObj)
                    with self.lock:
                        self.blocos.add(blocoObj.getId())

                    print(f"[{self.id}] Recebeu bloco {blocoObj.getId()} de {peer['id']}")
                    break
            except Exception:
                continue

    def salvarBloco(self, bloco: Block):
        nomeArquivo = os.path.join(PASTA_BLOCOS, f"block_{bloco.getId()}")
        try:
            with open(nomeArquivo, "wb") as f:
                f.write(bloco.getData())
        except Exception as e:
            print(f"[{self.id}] Erro ao salvar bloco {bloco.getId()}: {e}")

    def lerBloco(self, blocoId) -> Block:
        nomeArquivo = os.path.join(PASTA_BLOCOS, f"block_{blocoId}")
        try:
            with open(nomeArquivo, "rb") as f:
                conteudo = f.read()
                return Block(blocoId, conteudo)
        except Exception:
            return Block(blocoId, b"")

    def possuiTodosBlocos(self):
        return len(self.blocos) == self.totalBlocos