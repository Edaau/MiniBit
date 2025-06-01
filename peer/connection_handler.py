import threading
import socket
import json

class ConnectionHandler:
    def __init__(self, peerId, ip, port, blocos, pasta):
        self.peerId = peerId
        self.ip = ip
        self.port = port
        self.blocos = blocos
        self.pasta = pasta
        self.lock = threading.Lock()

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
                if blocoId is None:
                    return

                if blocoId in self.blocos:
                    conteudo = self.lerBloco(blocoId)
                    resposta = {"bloco": blocoId, "dados": conteudo}
                    conn.sendall(json.dumps(resposta).encode())
        except Exception as e:
            print(f"[{self.peerId}] Erro ao tratar conexao: {e}")

    def lerBloco(self, blocoId):
        try:
            with open(f"{self.pasta}/block_{blocoId}", "r") as f:
                return f.read()
        except:
            return "DADOS_FAKE"