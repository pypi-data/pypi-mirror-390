class Procedimento:

    def __init__(self, codigo, nome, status, senha, quantidade_solicitada,
                 valor_solicitado, quantidade_autorizada, valor_autorizado,
                 motivo_negativa):
        self.codigo = codigo
        self.nome = nome
        self.status = status
        self.senha = senha
        self.quantidade_solicitada = quantidade_solicitada
        self.valor_solicitado = valor_solicitado
        self.quantidade_autorizada = quantidade_autorizada
        self.valor_autorizado = valor_autorizado
        self.motivo_negativa = motivo_negativa