class RarestFirst:
    def init(self):
        self.peerBlocks = {}  # blocos de cada peer

    def updatePeerBlocks(self, peerId, blocos):
        self.peerBlocks[peerId] = blocos

    def escolherBlocoRaro(self, blocosQueTenho):
        contador = {}     # vai ser utilizado p/ contar a ocorrência de cada bloco disponível pra ver qual é o mais raro
        if not self.peerBlocks:
            return None

        for blocos in self.peerBlocks.values():
            for bloco in blocos:
                if bloco not in blocosQueTenho:
                    contador[bloco] = contador.get(bloco, 0) + 1

        if not contador: # Caso nenhum bloco novo seja encontrado nos peers
            return None

        blocoMaisRaroId = min(contador, key=contador.get)        # id do bloco com a menor contagem (mais raro)
        return blocoMaisRaroId

    def contarBlocosRaros(self, blocosQueTenho, blocosPeer):
        contador = {}
        for blocos in self.peerBlocks.values():
            for bloco in blocos:
                if bloco not in blocosQueTenho:                 # Considera apenas blocos que eu não tenho
                    contador[bloco] = contador.get(bloco, 0) + 1

        score = sum(1 for b in blocosPeer if b in contador)
        return score