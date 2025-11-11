import json
import requests
from datetime import datetime
from portal_facil_sdk.services.cache_service import CacheService


class Token:
    
    def __init__(self, **kwargs):
        self.access_token = kwargs.get('access_token')
        self.requested_at = self._converter_data(kwargs.get('.issued'))
        self.expires_in = self._converter_data(kwargs.get('.expires'))
    
    @property   
    def is_expired(self) -> bool:
        return datetime.now() > self.expires_in

    def _converter_data(self, data: str) -> datetime:
        return datetime.strptime(data, '%a, %d %b %Y %H:%M:%S %Z')
    
    
class CrmProviderException(Exception):
    
    def __init__(self, message: str):
        self.message = message
                   
            
class CrmProvider:
    _timeout = 10
    
    def __init__(
            self, 
            app_key: str, 
            base_url: str, 
            username: str, 
            password: str, 
            tipo_entidade_padrao: int, 
            origem_padrao: int,
            subcategoria_padrao: int,
            cache: CacheService
    ):
        self._cache = cache
        self._app_key = app_key
        self._base_url = base_url
        self._username = username
        self._password = password
        self._tipo_entidade_padrao = tipo_entidade_padrao
        self._origem_padrao = origem_padrao
        self._subcategoria_padrao = subcategoria_padrao
    
    def obter_beneficiario(self, doc: str) -> dict:
        url = f'{self._base_url}/api/integracao/beneficiario/getbychave?chave={doc}'
        headers = self._get_headers()
        response = self._get(url, headers)
        
        if response.status_code != 200:
            raise CrmProviderException(f'Erro ao obter beneficiário: {response.status_code} - {response.text}')
        
        try:
            return response.json()
        
        except json.JSONDecodeError:
            raise CrmProviderException(f'Erro ao decodificar a resposta JSON: {response.text}')
        
    def obter_guias(self, codigo_beneficiario: str, dias: int=30) -> dict:
        url = f'{self._base_url}/api/integracao/beneficiario/getguias?codigoBeneficiario={codigo_beneficiario}&dias={dias}'
        headers = self._get_headers()
        response = self._get(url, headers)
        
        if response.status_code != 200:
            raise CrmProviderException(f'Erro ao obter guias: {response.status_code} - {response.text}')
        
        try:
            return response.json()
        
        except json.JSONDecodeError:
            raise CrmProviderException(f'Erro ao decodificar a resposta JSON: {response.text}')
        
    def obter_procedimentos(self, codigo_beneficiario: str, numero_guia_operador: int, numero_guia_prestador: str=None) -> dict:
        url = f'{self._base_url}/api/integracao/beneficiario/getprocedimentos?codigoBeneficiario={codigo_beneficiario}&numguiaope={numero_guia_operador}&numguiaprest={numero_guia_prestador}'
        headers = self._get_headers()
        response = self._get(url, headers)
        
        if response.status_code != 200:
            raise CrmProviderException(f'Erro ao obter guias: {response.status_code} - {response.text}')
        
        try:
            return response.json()
        
        except json.JSONDecodeError:
            raise CrmProviderException(f'Erro ao decodificar a resposta JSON: {response.text}')
    
    def abrir_ticket(self, beneficiario_id, telefone, origem_id=None, sub_categoria_id=None) -> dict:
        url = f'{self._base_url}/api/integracao/crm/abrirchamado/'
        headers = self._get_headers(add_content_type_json=True)

        if not origem_id:
            origem_id = self._origem_padrao
        
        if not sub_categoria_id:        
            sub_categoria_id = self._subcategoria_padrao

        payload = json.dumps({
            'IdentificadorEntidade': beneficiario_id,
            'TipoEntidade': self._tipo_entidade_padrao,
            'Titulo': 'Ticket origem telefonia',
            'Descricao': f'Telefone origem: {telefone}',
            'OrigemId': origem_id,
            'SubCategoriaId': sub_categoria_id,
        })
        response = self._post(url, headers, payload)
        
        if response.status_code != 200:
            raise CrmProviderException(f'Erro ao abrir ticket: {response.status_code} - {response.text}')
        
        return response.json()
    
    def adicionar_anotacao(self, ticket_id, protocolo, anotacao) -> dict:
        url = f'{self._base_url}/api/integracao/crm/adicionaranotacao/'
        headers = self._get_headers(add_content_type_json=True)
        payload = json.dumps({
            'IdChamado': ticket_id,
            'NumeroProtocolo': protocolo,
            'Anotacao': anotacao
        })
        response = self._post(url, headers, payload)
        
        if response.status_code != 200:
            raise CrmProviderException(f'Erro ao adicionar uma anotacao: {response.status_code} - {response.text}')
    
    def encerrar_chamado(self, ticket_id, protocolo) -> dict:
        url = f'{self._base_url}/api/integracao/crm/encerrarchamado/'
        headers = self._get_headers(add_content_type_json=True)
        payload = json.dumps({
            'IdChamado': ticket_id,
            'NumeroProtocolo': protocolo,
            'EncerrarSomenteContato': False
        })
        response = self._post(url, headers, payload)
        
        if response.status_code != 200:
            raise CrmProviderException(f'Erro ao encerrar o chamado: {response.status_code} - {response.text}')

    def _get_headers(self, add_content_type_json=True) -> dict:
        headers = {
            'Authorization': f'Bearer {self._get_access_token()}',
            'X-API-KEY': self._app_key
        }
        
        if add_content_type_json:
            headers['Content-Type'] = 'application/json'
            
        return headers
    
    def _get_access_token(self) -> str:
        token_data = self._cache.get()
        
        if token_data:
            token = Token(**token_data)
            
            if not token.is_expired:
                return token.access_token
        
        token = self._get_new_token()
        return token.access_token
    
    def _get_new_token(self) -> Token:
        token_data = self._get_new_token_data()
        self._cache.save(token_data)
        return Token(**token_data)
    
    def _get_new_token_data(self) -> dict:
        url = f'{self._base_url}/token'
        payload = {
            'username': self._username,
            'password': self._password,
            'grant_type': 'password'
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }
        response = self._post(url, headers, payload)
        
        if response.status_code != 200:
            raise CrmProviderException(f'Erro ao obter token: {response.status_code} - {response.text}')
        
        return response.json()
    
    def _get(self, url, headers) -> requests.Response:
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=self._timeout
            )
            return response

        except requests.exceptions.Timeout:
            raise CrmProviderException('A requisição excedeu o tempo limite.')
    
    def _post(self, url, headers, payload) -> requests.Response:
        
        try:
            response = requests.post(
                url,
                headers=headers,
                data=payload,
                timeout=self._timeout
            )
            return response

        except requests.exceptions.Timeout:
            raise CrmProviderException('A requisição excedeu o tempo limite.')
    