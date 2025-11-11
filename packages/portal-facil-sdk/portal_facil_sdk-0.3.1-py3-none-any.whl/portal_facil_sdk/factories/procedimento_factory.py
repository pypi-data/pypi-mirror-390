from portal_facil_sdk.entities.procedimento import Procedimento


def criar_procedimento(data: dict) -> 'Procedimento':

    return Procedimento(
        codigo=data.get('codigo'),
        nome=data.get('nome'),
        status=data.get('status'),
        senha=data.get('senha'),
        quantidade_solicitada=data.get('quantidadeSolicitada'),
        valor_solicitado=data.get('valorSolicitado'),
        quantidade_autorizada=data.get('quantidadeAutorizada'),
        valor_autorizado=data.get('valorAutorizado'),
        motivo_negativa=data.get('motivoNegativa'),
    )