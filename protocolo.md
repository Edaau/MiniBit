# Protocolo de Comunicação P2P

Este documento descreve tecnicamente o protocolo de comunicação adotado no sistema P2P, incluindo as mensagens trocadas, os mecanismos de seleção de blocos, critérios de desbloqueio de peers e demais detalhes técnicos da operação da rede.

## 1. Estrutura Geral do Sistema

- A rede é composta por múltiplos peers e um tracker central.
- O tracker é responsável apenas pela distribuição inicial dos blocos e pelo fornecimento da lista de peers. Ele **não coordena** a troca de blocos entre os peers.
- Os peers se comunicam diretamente entre si via conexões socket TCP para realizar a troca de blocos.

---

## 2. Registro e Descoberta de Peers

### 2.1. Registro

Ao iniciar, um peer se registra no tracker, informando seu ID, IP, porta e lista de blocos que possui.

**Mensagem enviada do peer ao tracker:**

```json
{
  "id": "peer7",
  "ip": "127.0.0.1",
  "port": 9007,
  "blocks": [12, 45, 76, 140]
}
```

### 2.2. Resposta do Tracker

O tracker responde com a lista de todos os peers conhecidos no momento, incluindo o próprio tracker (se atuando como seeder).

```json
[
  {"id": "peer1", "ip": "127.0.0.1", "port": 9001, "blocks": [0, 5, 8, 12]},
  {"id": "peer3", "ip": "127.0.0.1", "port": 9003, "blocks": [22, 34, 44]},
  {"id": "tracker", "ip": "127.0.0.1", "port": 9000, "blocks": [0, 1, ..., 255]}
]
```

### 2.3. Reconsulta

Periodicamente (a cada 3 rodadas de troca), o peer reconsulta o tracker, enviando sua lista atualizada de blocos e recebendo uma nova lista de peers, com suas respectivas listas de blocos. Essa operação serve para manter a visão da rede atualizada e alimentar as estratégias de troca.

---

## 3. Protocolo de Troca de Blocos

### 3.1. Solicitação de Bloco

Quando um peer deseja um bloco, ele abre uma conexão TCP com outro peer desbloqueado e envia:

```json
{
  "bloco": 42,
  "peerId": "peer7"
}
```

### 3.2. Resposta

Se o peer tiver o bloco e o solicitante estiver desbloqueado, ele responde com:

```json
{
  "id": 42,
  "data": "<base64 ou bytes em string>"
}
```

---

## 4. Estratégia de Seleção de Blocos - Rarest First

A estratégia de **Rarest First** determina qual bloco será solicitado de um peer desbloqueado com base em sua raridade:

- O peer mantém um mapa de blocos por peer, atualizado a cada reconsulta ao tracker.
- Entre os blocos que ainda precisa, o peer identifica aqueles que são menos frequentes entre os conhecidos.
- Dentre os blocos que um peer desbloqueado possui e que são raros, o mais raro é escolhido para ser solicitado.

Esse mecanismo garante uma distribuição mais equilibrada dos blocos pela rede, evitando concentração.

---

## 5. Estratégia de Desbloqueio de Peers - Tit-for-Tat

A cada 10 segundos, o peer atualiza sua lista de peers desbloqueados, utilizando a seguinte lógica:

- **Top 4 fixos**: São os 4 peers com maior quantidade de blocos raros (com relação ao que o peer ainda não possui).
- **Unchoke otimista**: Um peer aleatório é desbloqueado temporariamente para permitir trocas mesmo com peers ainda não testados.

### Critérios:

- Se o peer sorteado para unchoke otimista possuir blocos raros suficientes, ele pode substituir o peer com pior score entre os 4 fixos.
- Caso contrário, ele permanece desbloqueado apenas de forma temporária naquela rodada.
- No total, no máximo 5 peers podem estar desbloqueados por rodada (4 fixos + 1 otimista).

---

## 6. Estado Seeder

Quando um peer completa todos os blocos:

- Ele **continua aceitando** conexões e respondendo a solicitações de blocos.
- Não solicita mais blocos nem executa o processo de Tit-for-Tat.
- Esse comportamento contribui para a descentralização e reduz a carga no tracker.

---

## 7. Considerações Técnicas

- A comunicação entre peers ocorre exclusivamente via TCP.
- A transferência de blocos é feita via JSON serializado.
- A reconstrução do arquivo final considera a extensão original (detectada a partir de `extensao.txt`).
- Toda operação de recebimento de blocos é registrada com log detalhado incluindo o ID do bloco, o peer remetente e o caminho salvo.
- A falha ao receber blocos ou conectar com peers é tolerada, com tentativas periódicas em cada nova rodada.

---

## 8. Logs e Persistência

O sistema mantém:

- Arquivo de log `file_manager.log` com todas as operações de leitura e escrita de blocos.
- Arquivo reconstruído ao final (`arquivo_final_peer_X.extensao`).
- Pastas separadas por peer contendo os blocos recebidos.

---