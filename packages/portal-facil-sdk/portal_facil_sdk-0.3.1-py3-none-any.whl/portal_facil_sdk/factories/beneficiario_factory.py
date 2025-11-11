from portal_facil_sdk.entities.beneficiario import Beneficiario


def criar_beneficiario(data) -> Beneficiario:
    
    if type(data) == list and len(data) > 0:
        data = data[0]
    
    elif type(data) == dict:
        data = data
    
    else:
        raise ValueError('Dados inválidos para criar beneficiário')
    
    return Beneficiario(
        codigo=data.get('codigo', ''),
        cpf=data.get('cpf', ''),
        nome=data.get('nome', '')
    )
    
    