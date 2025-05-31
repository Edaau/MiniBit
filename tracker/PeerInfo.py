# Representa um peer no sistema
class PeerInfo:
    def __init__(self, peerId, ip, port, blocks):
        self.id = peerId          # Identificador unico do peer (string)
        self.ip = ip              # Endereco IP (string)
        self.port = port          # Porta de conexao (int)
        self.blocks = blocks      # Lista de blocos que o peer possui (lista de int)

    def getDict(self):
        # Retorna representacao em dicionario para enviar por JSON
        return {
            "id": self.id,
            "ip": self.ip,
            "port": self.port,
            "blocks": self.blocks
        }

    @staticmethod
    def setDict(data):
        # Cria objeto PeerInfo a partir de um dicionario (JSON recebido)
        return PeerInfo(
            peerId=data.get("id"),
            ip=data.get("ip"),
            port=data.get("port"),
            blocks=data.get("blocks", [])
        )