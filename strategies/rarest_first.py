class RarestFirst:
    def __init__(self):
        self.peerBlocks = {} # blocos de cada peer

    def updatePeerBlocks(self, peerId, blocos): 
        self.peerBlocks[peerId] =blocos

    def escolherBlocoRaro(self, blocosQueTenho): 
        contador = {} # vai ser utilizado p/ contar a ocorrência de cada bloco disponível pra ver qual é o mais raro
        if not self.peerBlocks: 
            return None

        for peer_id, blocos_do_peer in self.peerBlocks.items():
            for bloco_id in blocos_do_peer:
                if bloco_id not in blocosQueTenho : # Considera apenas blocos que eu não tenho
                    if bloco_id not in contador:
                        contador[bloco_id] = 0
                    contador[bloco_id] += 1
        

        if not contador: # Caso nenhum bloco novo seja encontrado nos peers
            return None  
        blocoMaisRaroId = min(contador, key=contador.get)     # id do bloco com a menor contagem (mais raro)
        return blocoMaisRaroId