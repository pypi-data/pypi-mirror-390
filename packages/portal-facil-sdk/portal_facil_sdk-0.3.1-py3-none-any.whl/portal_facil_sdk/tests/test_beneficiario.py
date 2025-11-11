from unittest import TestCase
from portal_facil_sdk.entities.beneficiario import Beneficiario
from portal_facil_sdk.factories.beneficiario_factory import criar_beneficiario
from portal_facil_sdk.tests.constants import DADOS_BENEFICIARIO


class TestBeneficiario(TestCase):
    
    def test_beneficiario_entity(self):
        beneficiario = Beneficiario(
            codigo='000002-7',
            cpf='035.710.586-90',
            nome='BENEFICIARIO GENERICO',
        )
        self.assertEqual(beneficiario.codigo, '000002-7')
        self.assertEqual(beneficiario.cpf, '035.710.586-90')
        self.assertEqual(beneficiario.nome, 'BENEFICIARIO GENERICO')
    
    def test_beneficiario_factory(self):
        received_data = DADOS_BENEFICIARIO
        beneficiario = criar_beneficiario(received_data)
        self.assertIsInstance(beneficiario, Beneficiario)
        