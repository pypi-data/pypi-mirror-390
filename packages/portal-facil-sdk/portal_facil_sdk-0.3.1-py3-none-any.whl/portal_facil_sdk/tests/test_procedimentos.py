from unittest import TestCase
from portal_facil_sdk.entities.procedimento import Procedimento
from portal_facil_sdk.factories.procedimento_factory import criar_procedimento
from portal_facil_sdk.tests.constants import DADOS_PROCEDIMENTOS


class ProcedimentoTestCase(TestCase):
    
    def test_procedimento_entity(self):
        procedimento = Procedimento(
            codigo= '4.10.01.10-9', 
            nome= 'TC - ABDOME SUPERIOR ', 
            status= 'Senha cancelada', 
            senha= None, 
            quantidade_solicitada= 1.0, 
            valor_solicitado= 115.08, 
            quantidade_autorizada= 0.0, 
            valor_autorizado= 0.0, 
            motivo_negativa= None
        )
        self.assertEqual(procedimento.codigo, '4.10.01.10-9')
        self.assertEqual(procedimento.nome, 'TC - ABDOME SUPERIOR ')
        self.assertEqual(procedimento.status, 'Senha cancelada')
        self.assertEqual(procedimento.quantidade_solicitada, 1.0)
        self.assertEqual(procedimento.valor_solicitado, 115.08)
        self.assertEqual(procedimento.quantidade_autorizada, 0.0)
        self.assertEqual(procedimento.valor_autorizado, 0.0)
        self.assertIsNone(procedimento.senha)
        self.assertIsNone(procedimento.motivo_negativa)
    
    def test_criar_procedimento_factory(self):
        received_data = DADOS_PROCEDIMENTOS[0]
        procedimento = criar_procedimento(received_data)
        self.assertIsInstance(procedimento, Procedimento)