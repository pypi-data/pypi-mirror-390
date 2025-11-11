from unittest import TestCase
from unittest.mock import MagicMock
from portal_facil_sdk.controllers.atendimento_controller import AtendimentoController
from portal_facil_sdk.entities.beneficiario import Beneficiario
from portal_facil_sdk.entities.guia_beneficiario import GuiaBeneficiario
from portal_facil_sdk.entities.procedimento import Procedimento
from portal_facil_sdk.entities.ticket import Ticket
from portal_facil_sdk.tests.constants import (
    DADOS_BENEFICIARIO, 
    DADOS_TICKET, 
    DADOS_GUIA_BENEFICIARIO,
    DADOS_PROCEDIMENTOS
)

class TestAtendimentoController(TestCase):
    
    def setUp(self):
        provider = MagicMock()
        provider.obter_beneficiario.return_value = DADOS_BENEFICIARIO
        provider.abrir_ticket.return_value = DADOS_TICKET
        provider.obter_guias.return_value = DADOS_GUIA_BENEFICIARIO
        provider.obter_procedimentos.return_value = DADOS_PROCEDIMENTOS
        self.controller = AtendimentoController(provider)

    def test_consultar_beneficiario(self):
        doc = '0000027'
        beneficiario = self.controller.consultar_beneficiario(doc)
        self.assertIsInstance(beneficiario, Beneficiario)
        self.controller._provider.obter_beneficiario.return_value = []
        self.assertRaises(ValueError, self.controller.consultar_beneficiario, doc)

    def test_abrir_chamado(self):
        beneficiario = Beneficiario(
            codigo='0000027', nome='BENEFICIARIO GENERICO', cpf='035.710.586-90'
        )
        telefone = '1137092380'
        ticket = self.controller.abrir_chamado(beneficiario, telefone)
        self.assertIsInstance(ticket, Ticket)
    
    def test_obter_guias_beneficiario(self):
        beneficiario = Beneficiario(
            codigo='0000027', nome='BENEFICIARIO GENERICO', cpf='035.710.586-90'
        )
        guias = self.controller.obter_guias_beneficiario(beneficiario)
        self.assertIsInstance(guias, list)

        for guia in guias:
            self.assertIsInstance(guia, GuiaBeneficiario)
    
    def test_obter_procedimentos(self):
        beneficiario = Beneficiario(
            codigo='0000027', nome='BENEFICIARIO GENERICO', cpf='035.710.586-90'
        )
        numero_guia_operador = 509470
        numero_guia_prestador = '00101206102545279301'
        procedimentos = self.controller.obter_procedimentos(
            beneficiario, 
            numero_guia_operador, 
            numero_guia_prestador
        )
        self.assertIsInstance(procedimentos, list)
        self.assertIsInstance(procedimentos[0], Procedimento)