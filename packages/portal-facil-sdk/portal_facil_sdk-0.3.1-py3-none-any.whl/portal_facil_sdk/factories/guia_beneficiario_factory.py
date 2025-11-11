from portal_facil_sdk.entities.guia_beneficiario import GuiaBeneficiario


def criar_guia_beneficiario(data: dict) -> GuiaBeneficiario:
    return GuiaBeneficiario(
        indice=data.get('indice'),
        numero_guia_operadora=data.get('numeroGuiaOperadora'),
        numero_guia_prestador=data.get('numeroGuiaPrestador'),
        tipo=data.get('tipo'),
        status=data.get('status'),
        codigo_prestador_solicitante=data.get('codigoPrestadorSolicitante'),
        nome_prestador_solicitante=data.get('nomePrestadorSolicitante'),
        local_atendimento=data.get('localAtendimento'),
        codigo_prestador_executante=data.get('codigoPrestadorExecutante'),
        nome_prestador_executante=data.get('nomePrestadorExecutante'),
        senha=data.get('senha'),
        data_liberacao=data.get('dataLiberacao'),
        data_realizacao=data.get('dataRealizacao'),
        data_alta=data.get('dataAlta'),
        aguardando_documentacao=data.get('aguardandoDocumentacao'),
        aguardando_beneficiario=data.get('aguardandoBeneficiario'),
        data_inclusao=data.get('dataInclusao'),
        status_detalhado=data.get('statusDetalhado')
    )