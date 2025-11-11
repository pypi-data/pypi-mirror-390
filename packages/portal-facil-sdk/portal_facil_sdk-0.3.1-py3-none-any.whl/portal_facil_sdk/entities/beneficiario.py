class Beneficiario:
    
    def __init__(self, codigo: str, cpf: str, nome: str):
        self.codigo = codigo
        self.cpf = cpf
        self.nome = nome
    
    def __str__(self):
        return f'Beneficiário(codigo={self.codigo}, nome={self.nome})'