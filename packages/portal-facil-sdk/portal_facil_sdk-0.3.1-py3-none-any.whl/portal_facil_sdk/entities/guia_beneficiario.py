class GuiaBeneficiario:

    def __init__(self, indice, numero_guia_operadora, numero_guia_prestador, tipo, status,
                 codigo_prestador_solicitante, nome_prestador_solicitante, local_atendimento,
                 codigo_prestador_executante, nome_prestador_executante, senha,
                 data_liberacao, data_realizacao, data_alta,
                 aguardando_documentacao, aguardando_beneficiario,
                 data_inclusao, status_detalhado):
        self.indice = indice
        self.numero_guia_operadora = numero_guia_operadora
        self.numero_guia_prestador = numero_guia_prestador
        self.tipo = tipo
        self.status = status
        self.codigo_prestador_solicitante = codigo_prestador_solicitante
        self.nome_prestador_solicitante = nome_prestador_solicitante
        self.local_atendimento = local_atendimento
        self.codigo_prestador_executante = codigo_prestador_executante
        self.nome_prestador_executante = nome_prestador_executante
        self.senha = senha
        self.data_liberacao = data_liberacao
        self.data_realizacao = data_realizacao
        self.data_alta = data_alta
        self.aguardando_documentacao = aguardando_documentacao
        self.aguardando_beneficiario = aguardando_beneficiario
        self.data_inclusao = data_inclusao
        self.status_detalhado = status_detalhado