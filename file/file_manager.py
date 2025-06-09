import logging
import os
from tarfile import BLOCKSIZE

# Configura logs (adicione no topo do arquivo)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    filename='file_manager.log'
)

def splitFile(inputFilePath: str, outputDir: str) -> int:
    try:
        if not os.path.exists(inputFilePath):
            logging.error(f"Arquivo não encontrado: {inputFilePath}")
            return 0
        
        os.makedirs(outputDir, exist_ok=True)
        totalBlocks = 0

        with open(inputFilePath, 'rb') as f:
            while True:
                block = f.read(BLOCKSIZE)
                if not block:
                    break
                blockName = f"block_{totalBlocks:04d}"  # Formato block_0001
                with open(os.path.join(outputDir, blockName), 'wb') as bf:
                    bf.write(block)
                logging.info(f"Bloco {blockName} criado em {outputDir}")
                totalBlocks += 1

        return totalBlocks

    except Exception as e:
        logging.error(f"Falha ao dividir arquivo: {e}")
        return 0

# Adicione logs similares em mergeBlocks e outras funções!