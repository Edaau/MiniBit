import socket
import threading
import json
import time
import os
import sys
from tracker.PeerInfo import PeerInfo
from file.block import Block
from file.file_manager import FileManager
from strategies.rarest_first import RarestFirst
from peer.tit_for_tat import TitForTatManager
import random

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
        self.topPeers = []

        self.pastaBlocos = f"blocos_recebidos_Peer{self.id}"
        if not os.path.exists(self.pastaBlocos):
            os.makedirs(self.pastaBlocos)

        self.fileManager = FileManager(None, self.pastaBlocos)
        self.titForTat.configurarRarest(self.rarest)

    def start(self):
        print(f"[{self.id}] Iniciando peer em {self.ip}:{self.port}")
        self.registrarNoTracker()

        threadServidor = threading.Thread(target=self.escutarOutrosPeers)
        threadServidor.start()

        contador = 0
        while not self.possuiTodosBlocos():
            if contador % 3 == 0:
                self.reconsultarTracker()

            self.titForTat.atualizarUnchoke(self.blocos)
            self.trocarComPeers()
            self.titForTat.exibirProgresso(self.id, self.blocos, self.totalBlocos)
            self.mostrarPeersDesbloqueados()
            time.sleep(5)
            contador += 1

        print(f"[{self.id}] Arquivo completo! Todos os blocos foram recebidos.")
        self.fileManager.mergeBlocks(f"arquivo_final_peer_{self.id}.pdf")

    def registrarNoTracker(self):
        meuPeer = PeerInfo(self.id, self.ip, self.port, [])
        peerDict = meuPeer.getDict()

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.trackerIp, self.trackerPort))
                s.sendall(json.dumps(peerDict).encode())
                resposta = s.recv(8192)
                if not resposta:
                    print(f"[{self.id}] Resposta vazia do tracker")
                    return

                lista = json.loads(resposta.decode())
                self.listaPeers = lista
                print(f"[{self.id}] Tracker retornou {len(lista)} peer(s).")

                meusBlocos = next((p["blocks"] for p in lista if p["id"] == self.id), [])

                for bloco in meusBlocos:
                    try:
                        caminho = os.path.join("blocos_originais", f"block_{bloco:04d}")
                        with open(caminho, "rb") as f:
                            conteudo = f.read()
                            blocoObj = Block(bloco, conteudo)
                            self.salvarBloco(blocoObj, remetente="tracker")
                            self.blocos.add(bloco)
                            print(f"[{self.id}] Bloco inicial {bloco} carregado com {len(conteudo)} bytes.")
                    except Exception as e:
                        print(f"[{self.id}] Erro ao carregar bloco {bloco}: {e}")

                todosBlocos = []
                for p in lista:
                    self.rarest.updatePeerBlocks(p["id"], p["blocks"])
                    self.titForTat.atualizarPeerBlocks(p["id"], p["blocks"])
                    todosBlocos.extend(p["blocks"])
                self.totalBlocos = max(todosBlocos) + 1 if todosBlocos else 10

        except Exception as e:
            print(f"[{self.id}] Erro ao conectar no tracker: {e}")

    def reconsultarTracker(self):
        try:
            meuPeer = PeerInfo(self.id, self.ip, self.port, list(self.blocos))
            peerDict = meuPeer.getDict()
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.trackerIp, self.trackerPort))
                s.sendall(json.dumps(peerDict).encode())
                resposta = s.recv(8192)
                if not resposta:
                    return
                novaLista = json.loads(resposta.decode())

                for p in novaLista:
                    if p["id"] != self.id:
                        self.rarest.updatePeerBlocks(p["id"], p["blocks"])
                        self.titForTat.atualizarPeerBlocks(p["id"], p["blocks"])
                self.listaPeers = novaLista
                print(f"[{self.id}] Lista de peers atualizada: {len(self.listaPeers)}")
        except Exception as e:
            print(f"[{self.id}] Falha ao reconsultar tracker: {e}")

    def escutarOutrosPeers(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
                data = conn.recv(2048)
                if not data:
                    print(f"[{self.id}] Dados vazios recebidos de {peerIp}")
                    return

                try:
                    pedido = json.loads(data.decode())
                except Exception as e:
                    print(f"[{self.id}] Erro ao decodificar pedido JSON: {e}")
                    return

                blocoSolicitado = pedido.get("bloco")
                peerIdRemoto = pedido.get("peerId")

                print(f"[{self.id}] Pedido de bloco {blocoSolicitado} de {peerIdRemoto}")

                if self.id != "tracker" and not self.titForTat.estaDesbloqueado(peerIdRemoto):
                    print(f"[{self.id}] Peer {peerIdRemoto} bloqueado (Tit-for-Tat)")
                    return

                if blocoSolicitado in self.blocos:
                    bloco = self.lerBloco(blocoSolicitado)
                    resposta = bloco.getDict()
                    try:
                        conn.sendall(json.dumps(resposta).encode())
                        print(f"[{self.id}] Enviou bloco {bloco.getId()} para {peerIdRemoto}")
                    except Exception as e:
                        print(f"[{self.id}] Falha ao enviar bloco {bloco.getId()} para {peerIdRemoto}: {e}")

        except Exception as e:
            print(f"[{self.id}] Erro ao lidar com peer: {e}")

    def receber_tudo(self, sock):
        dados = b""
        while True:
            parte = sock.recv(4096)
            if not parte:
                break
            dados += parte
            if len(parte) < 4096:
                break
        return dados

    def trocarComPeers(self):
        peersDesbloqueados = [p for p in self.listaPeers if self.titForTat.estaDesbloqueado(p["id"])]
        random.shuffle(peersDesbloqueados)

        for peer in peersDesbloqueados:
            blocosPeer = peer.get("blocks", [])
            blocosFaltando = [b for b in blocosPeer if b not in self.blocos]
            if not blocosFaltando:
                continue

            bloco = random.choice(blocosFaltando)

            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(5)
                    s.connect((peer["ip"], peer["port"]))
                    pedido = {"bloco": bloco, "peerId": self.id}
                    s.sendall(json.dumps(pedido).encode())

                    resposta = self.receber_tudo(s)
                    if not resposta:
                        print(f"[{self.id}] Nenhuma resposta recebida de {peer['id']} ao solicitar bloco {bloco}")
                        continue

                    try:
                        dados = json.loads(resposta.decode())
                        blocoObj = Block.setDict(dados)
                        self.salvarBloco(blocoObj, remetente=peer["id"])
                        with self.lock:
                            self.blocos.add(blocoObj.getId())

                        print(f"[{self.id}] Recebeu bloco {blocoObj.getId()} de {peer['id']} ({len(blocoObj.getData())} bytes)")
                        break
                    except Exception as e:
                        print(f"[{self.id}] Erro ao processar resposta de {peer['id']} para bloco {bloco}: {e}")
                        continue
            except Exception as e:
                print(f"[{self.id}] Erro ao trocar bloco {bloco} com {peer['id']}: {e}")
                continue

    def salvarBloco(self, bloco: Block, remetente=None):
        try:
            self.fileManager.salvarBloco(bloco, remetente=remetente)
        except Exception as e:
            print(f"[{self.id}] Erro ao salvar bloco {bloco.getId()}: {e}")

    def lerBloco(self, blocoId) -> Block:
        try:
            return self.fileManager.lerBloco(blocoId)
        except Exception:
            return Block(blocoId, b"")

    def possuiTodosBlocos(self):
        return len(self.blocos) == self.totalBlocos

    def mostrarPeersDesbloqueados(self):
        desbloqueados = [peerId for peerId, status in self.titForTat.peerStatus.items() if status]
        print(f"[{self.id}] Peers desbloqueados atualmente: {desbloqueados}")

# Execucao: python Peer.py <peerId> <meu_ip> <minha_porta> <tracker_ip> <tracker_porta>
if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Uso: python main_peer.py <peerId> <meu_ip> <minha_porta> <tracker_ip> <tracker_porta>")
        sys.exit(1)

    peerId = sys.argv[1]
    ip = sys.argv[2]
    port = int(sys.argv[3])
    trackerIp = sys.argv[4]
    trackerPort = int(sys.argv[5])

    peer = Peer(peerId, ip, port, trackerIp, trackerPort)
    peer.start()
