import os
import logging
from file.block import Block  # Importa a classe Block

# Tamanho do bloco: 256 KB
BLOCO_TAMANHO = 256 * 1024

os.makedirs("logs", exist_ok=True)
# Configura logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    filename='logs/file_manager.log'
)

class FileManager:
    def _init_(self, inputFilePath=None, outputDir="blocos_recebidos"):
        self.inputFilePath = inputFilePath
        self.outputDir = outputDir
        self.blockSize = BLOCO_TAMANHO

        os.makedirs(self.outputDir, exist_ok=True)

    def splitFile(self):
        """
        Divide o arquivo original em blocos de 256 KB.
        Retorna o número total de blocos criados.
        """
        try:
            if not os.path.exists(self.inputFilePath):
                logging.error(f"Arquivo não encontrado: {self.inputFilePath}")
                return 0

            totalBlocks = 0

            with open(self.inputFilePath, 'rb') as f:
                while True:
                    data = f.read(self.blockSize)
                    if not data:
                        break

                    block = Block(totalBlocks, data)
                    blockName = f"block_{totalBlocks:04d}"
                    caminho = os.path.join(self.outputDir, blockName)

                    with open(caminho, 'wb') as bf:
                        bf.write(block.getData())

                    logging.info(f"Bloco {blockName} criado em {self.outputDir}")
                    totalBlocks += 1

            return totalBlocks

        except Exception as e:
            logging.error(f"Falha ao dividir arquivo: {e}")
            return 0

    def mergeBlocks(self, outputFilePath):
        """
        Junta todos os blocos em ordem e gera o arquivo final reconstruído.
        """
        try:
            blocos = sorted(
                [f for f in os.listdir(self.outputDir) if f.startswith("block_")]
            )

            with open(outputFilePath, 'wb') as saida:
                for blocoNome in blocos:
                    caminho = os.path.join(self.outputDir, blocoNome)
                    blocoId = int(blocoNome.split("_")[1])

                    with open(caminho, 'rb') as bf:
                        conteudo = bf.read()

                    bloco = Block(blocoId, conteudo)
                    saida.write(bloco.getData())

                    logging.info(f"Bloco {blocoNome} adicionado ao {outputFilePath}")

            logging.info(f"Arquivo reconstruído salvo em: {outputFilePath}")
        except Exception as e:
            logging.error(f"Erro ao reconstruir arquivo: {e}")

    def lerBloco(self, blocoId):
        try:
            nomeArquivo = os.path.join(self.outputDir, f"block_{blocoId:04d}")
            with open(nomeArquivo, "rb") as f:
                conteudo = f.read()
                return Block(blocoId, conteudo)
        except Exception as e:
            logging.error(f"Erro ao ler bloco {blocoId}: {e}")
            return Block(blocoId, b"")

    def salvarBloco(self, bloco, remetente=None):
        try:
            nomeArquivo = os.path.join(self.outputDir, f"block_{bloco.getId():04d}")
            with open(nomeArquivo, "wb") as f:
                f.write(bloco.getData())

            if remetente:
                logging.info(f"Bloco {bloco.getId()} salvo em {nomeArquivo} (recebido de {remetente})")
            else:
                logging.info(f"Bloco {bloco.getId()} salvo em {nomeArquivo}")
        except Exception as e:
            logging.error(f"Erro ao salvar bloco {bloco.getId()}: {e}")

    def lerBlocoOriginal(self, blocoId):
        try:
            caminho = os.path.join("blocos_originais", f"block_{blocoId:04d}")
            with open(caminho, "rb") as f:
                data = f.read()
            return Block(blocoId, data)
        except Exception as e:
            raise Exception(f"Erro ao ler bloco original {blocoId}: {e}")