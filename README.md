# MiniBit
Implementação de um Sistema de Compartilhamento Cooperativo de Arquivos com Estratégias Distribuídas

## Sistema P2P com Tit-for-Tat e Rarest First

Este projeto simula um sistema de compartilhamento de arquivos em um ambiente ponto a ponto (P2P), utilizando uma arquitetura centralizada de rastreamento (tracker) e estratégias de troca baseadas em Tit-for-Tat simplificado e Rarest First. Foi desenvolvido como trabalho final para a disciplina de Sistemas Distribuídos.

## Estrutura do Projeto

- `tracker/Tracker.py`: Gerencia os peers e distribui os blocos iniciais. Também age como seeder.
- `peer/Peer.py`: Representa um peer da rede, capaz de solicitar, enviar e armazenar blocos.
- `file/file_manager.py`: Lida com a divisão e reconstrução do arquivo.
- `file/block.py`: Define a estrutura dos blocos.
- `strategies/rarest_first.py`: Implementa o algoritmo Rarest First.
- `peer/tit_for_tat.py`: Implementa o algoritmo Tit-for-Tat simplificado.

## Funcionamento Geral

1. O tracker recebe um arquivo de entrada e o divide em blocos de 256 KB.
2. Cada novo peer se conecta ao tracker e recebe um subconjunto aleatório de 4 blocos.
3. O peer mantém uma lista de peers conhecidos e, a cada rodada, escolhe quais desbloquear usando Tit-for-Tat.
4. Os peers trocam blocos entre si com base em:
   - Rarest First: o peer tenta baixar o bloco mais raro disponível entre os peers desbloqueados.
   - Tit-for-Tat: até 4 peers são mantidos desbloqueados com base na raridade dos blocos; 1 peer é desbloqueado aleatoriamente por rodada.
5. Um peer que completou o arquivo continua servindo como seeder para novos peers que ingressarem posteriormente.

## Algoritmos de Troca

### Tit-for-Tat (adaptado)

- A cada 10 segundos, o peer desbloqueia 1 peer aleatório (optimistic unchoke).
- Caso o peer aleatório tenha blocos raros, ele pode ser promovido ao top 4.
- O top 4 é formado com os peers que possuem os blocos mais raros.
- Apenas peers desbloqueados podem participar das trocas.

### Rarest First

- A raridade de um bloco é definida com base nos peers conhecidos no momento através de um score.
- O bloco menos comum entre os peers desbloqueados é priorizado no download.

## Comunicação entre Peers

As mensagens entre peers seguem o seguinte formato JSON:

**Pedido de bloco**
```json
{
  "bloco": 42,
  "peerId": "peer3"
}
```

**Resposta com bloco**
```json
{
  "id": 42,
  "data": "<dados base64 ou binários codificados>"
}
```

## Execução

### Executar o Tracker (e Seeder)
```bash
python tracker/Tracker.py <ip> <porta> <caminho_do_arquivo>
```

Exemplo:
```bash
python tracker/Tracker.py 192.168.0.62 8000 video.mp4
```

### Executar um Peer
```bash
python peer/Peer.py <peerId> <meu_ip> <minha_porta> <ip_tracker> <porta_tracker>
```

Exemplo:
```bash
python peer/Peer.py 1 192.168.0.62 9001 192.168.0.62 8000
```

### Observação

A extensão do arquivo original é salva em `extensao.txt` para que os peers possam reconstruir o arquivo final corretamente.

## Resultados e Observações

- O sistema distribui o arquivo entre os peers ao longo de várias rodadas.
- A maior parte dos blocos é inicialmente recebida do tracker, mas com o tempo os peers trocam entre si.
- O uso combinado de Rarest First e Tit-for-Tat promove um equilíbrio entre distribuição eficiente e diversidade de fontes.
- Peers que finalizam o download continuam servindo blocos a novos peers.
- O log detalhado mostra a origem de cada bloco recebido, permitindo auditoria da troca.

## Dificuldades Enfrentadas

- Problemas iniciais na troca de blocos por socket, especialmente com arquivos grandes (256 KB).
- Necessidade de implementar um mecanismo robusto para leitura completa dos dados (`recv_tudo`).
- Correção da lógica do Tit-for-Tat para respeitar os limites do top 4 e do peer otimista.
- Garantir que peers continuem atuando como seeder após completar o download.
- A necessidade de reconectar ao tracker periodicamente para atualização da lista de peers.