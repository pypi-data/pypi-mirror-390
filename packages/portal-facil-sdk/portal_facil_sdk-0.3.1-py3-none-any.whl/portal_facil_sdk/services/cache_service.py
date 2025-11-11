import pickle
import json


class CacheService:
    
    def __init__(self, filename: str):
        self._filename = filename
    
    def get(self) -> dict:
        try:
            with open(self._filename, 'rb') as arquivo_pickle:
                data = pickle.load(arquivo_pickle)
                return json.loads(data) 
             
        except (FileNotFoundError, EOFError):
            ...

    def save(self, data: dict):
        with open(self._filename, 'wb') as arquivo_pickle:
            pickle.dump(json.dumps(data), arquivo_pickle)