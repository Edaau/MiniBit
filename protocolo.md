# Protocolo de Comunicação – MiniBit

Este documento descreve o protocolo de comunicação entre os componentes do sistema MiniBit: Tracker e Peers. O objetivo é garantir o entendimento unificado da troca de mensagens entre os participantes da rede P2P.

---

## 1. Comunicação entre Peer e Tracker

### 1.1. Conexão

- O Peer se conecta ao Tracker via **socket TCP**.
- O Tracker escuta conexões em um IP e porta específicos (ex: `192.168.0.62:8000`).

---

### 1.2. Registro do Peer

**Fluxo:**
1. O Peer envia um objeto JSON contendo seus dados.
2. O Tracker atribui um subconjunto aleatório de blocos a esse Peer (baseado no arquivo de origem).
3. O Tracker registra o Peer e retorna uma lista de outros peers ativos na rede.

**Formato da mensagem enviada pelo Peer:**

```json
{
  "id": "peer01",
  "ip": "192.168.0.62",
  "port": 9001,
  "blocks": []  
}
```

> O campo `blocks` é ignorado e substituído pelo Tracker com blocos sorteados automaticamente.

---

### 1.3. Resposta do Tracker

O Tracker responde com uma lista de até **4 peers aleatórios**, exceto se a rede tiver 5 ou menos peers (nesse caso, retorna todos disponíveis).

**Formato da resposta do Tracker:**

```json
[
  {
    "id": "peer02",
    "ip": "192.168.0.62",
    "port": 9002,
    "blocks": [0, 4, 5, 9]
  },
  {
    "id": "peer03",
    "ip": "192.168.0.62",
    "port": 9003,
    "blocks": [1, 3, 7, 10]
  }
]
```

---

## 2. Estrutura do objeto `PeerInfo`

Representa um peer ativo na rede. Essa estrutura é usada tanto pelo Tracker quanto pelos Peers para identificar outros participantes.

| Campo   | Tipo     | Descrição                           |
|---------|----------|-------------------------------------|
| id      | string   | Identificador único do peer         |
| ip      | string   | Endereço IP do peer                 |
| port    | inteiro  | Porta de escuta do peer             |
| blocks  | lista de inteiros | IDs dos blocos que o peer possui |

---

##  3. Distribuição de blocos

- O Tracker define o **número total de blocos** com base no tamanho real do arquivo de entrada.
- Cada peer, ao entrar na rede, recebe um subconjunto aleatório de blocos (sem repetição dentro de si).
- Blocos **podem se repetir entre peers diferentes**, o que é desejável para redundância.

---

##  4. Considerações

- O protocolo é simples, baseado em troca de **objetos JSON serializados via TCP**.
- O Tracker **não mantém conexões abertas** com os peers após o registro inicial.
- Toda a lógica de troca de blocos, rarest first e tit-for-tat ocorre **entre os peers**, não no Tracker.
- O Tracker **não armazena o conteúdo dos blocos**, apenas os IDs.

---


---