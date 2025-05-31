import base64

class Block:
    def __init__(self, blockId: int, data: bytes):
        self.id = blockId 
        self.data = data 

    def getId(self):
        return self.id

    def getData(self):
        return self.data

    def getDict(self):   #Retorna um dicionário q converte dados binários para base64
        return {
            "id": self.id,  
            "data": base64.b64encode(self.data).decode("utf-8")
        }

    @staticmethod
    def setDict(data: dict):    
        #Cria uma instância de Block a partir de um dicionário, convertendo base64 de volta para bytes
        blockId = data.get("id")
        base64Data = data.get("data")
        if blockId is None:
            raise ValueError("ID não pode ser None")

        if base64Data is None: #ver se existe algum dado
            decodedData = b"" 
        else:
            try:
                decodedData = base64.b64decode(base64Data.encode("utf-8"))

            except Exception as e:
                raise ValueError(f"Erro ao decodificar dados base64: {e}")
        

        return Block(blockId, decodedData)