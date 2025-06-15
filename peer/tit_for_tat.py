import random
import time
from strategies.rarest_first import RarestFirst

class TitForTatManager:
    def __init__(self):
        self.peerStatus = {}  # {peerId: True/False}
        self.peersConhecidos = {}  # {peerId: [blocos]}
        self.ultimoUpdate = 0
        self.rarest = None

    def configurarRarest(self, rarest: RarestFirst):
        self.rarest = rarest

    def atualizarPeerBlocks(self, peerId, blocos):
        self.peersConhecidos[peerId] = blocos

    def atualizarUnchoke(self, blocosQueTenho):
        agora = time.time()
        if agora - self.ultimoUpdate < 10:
            return
        self.ultimoUpdate = agora

        if not self.rarest or not self.peersConhecidos:
            return

        # Escolhe o peer otimista (aleatório)
        todosPeers = list(self.peersConhecidos.keys())
        if not todosPeers:
            return

        otimista = random.choice(todosPeers)
        scoreOtimista = self.rarest.contarBlocosRaros(blocosQueTenho, self.peersConhecidos.get(otimista, []))
        promovido = False

        # Calcula os scores dos peers restantes (sem o otimista, por enquanto)
        scores = []
        for peerId, blocos in self.peersConhecidos.items():
            if peerId == otimista:
                continue
            score = self.rarest.contarBlocosRaros(blocosQueTenho, blocos)
            scores.append((peerId, score))

        # Ordena por score decrescente (mais blocos raros primeiro)
        scores.sort(key=lambda x: x[1], reverse=True)
        top4 = [peerId for peerId, _ in scores[:4]]

        # Se o otimista tiver blocos raros, ele pode ser promovido a fixo
        if scoreOtimista > 0:
            if otimista not in top4:
                if len(top4) == 4:
                    top4.pop()  # remove o último para dar espaço
                top4.append(otimista)
                promovido = True

        # Lista final: 4 fixos + 1 otimista (se não estiver entre os fixos)
        desbloqueados = set(top4)
        if not promovido:
            desbloqueados.add(otimista)

        self.peerStatus = {peerId: (peerId in desbloqueados) for peerId in self.peersConhecidos}

        print("[TIT-FOR-TAT] Peers desbloqueados nesta rodada:", list(desbloqueados))
        print("[TIT-FOR-TAT] Top 4 (baseado em blocos raros):", top4)
        print("[TIT-FOR-TAT] Optimistic Unchoke:", otimista, "(fixo)" if promovido else "(temporário)")

    def estaDesbloqueado(self, peerId):
        return self.peerStatus.get(peerId, False)

    def exibirProgresso(self, peerId, blocosQueTenho, totalBlocos):
        print(f"[PROGRESSO] Peer {peerId}: {len(blocosQueTenho)} blocos / {totalBlocos} blocos")