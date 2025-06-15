import random
import time

class TitForTatManager:
    def __init__(self):
        self.peerStatus = {} #desbloqueado ou nao
        self.lastUpload = {} #timestamp do ultimo envio

    def atualizarUpload(self, peerId):
        self.lastUpload[peerId] = time.time()

    def selecionarPeersParaUnchoke(self):

        #desbloqueia os 4 peers com mais uploads recentes
        peersOrdenados = sorted(self.lastUpload.items(), key=lambda x: x[1], reverse=True)
        top4 = [peer[0] for peer in peersOrdenados[:4]]

        #vai escolher 1 peer aleatorio para unchoke
        outros = list(set(self.lastUpload.keys()) - set(top4))
        otimista = random.choice(outros) if outros else None

        desbloqueados = top4.copy()
        if otimista:
            desbloqueados.append(otimista)

        #atualiza status
        self.peerStatus = {peer: (peer in desbloqueados) for peer in self.lastUpload.keys()}
        return desbloqueados

    def estaDesbloqueado(self, peerId):
        return self.peerStatus.get(peerId, False)