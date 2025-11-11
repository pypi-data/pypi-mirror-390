from unittest import TestCase
from portal_facil_sdk.entities.guia_beneficiario import GuiaBeneficiario
from portal_facil_sdk.factories.guia_beneficiario_factory import criar_guia_beneficiario
from portal_facil_sdk.tests.constants import DADOS_GUIA_BENEFICIARIO


class GuiaBeneficiarioTest(TestCase):
    
    def test_guia_beneficiario_entity(self):
        guia = GuiaBeneficiario(
           indice=1, 
           numero_guia_operadora=509486, 
           numero_guia_prestador="00363206102545280901", 
           tipo="SP/SADT", 
           status="Solicitação cancelada", 
           codigo_prestador_solicitante=None, 
           nome_prestador_solicitante=None, 
           local_atendimento="MILLENNIUM EMERGENCIAS MEDICAS LTDA", 
           codigo_prestador_executante=None, 
           nome_prestador_executante=None, 
           senha=None, 
           data_liberacao="2025-10-06T00:00:00", 
           data_realizacao="2025-10-06T00:00:00", 
           data_alta=None, 
           aguardando_documentacao="Não", 
           aguardando_beneficiario="Não", 
           data_inclusao="2025-10-06T08:23:29", 
           status_detalhado=None
        )
        self.assertEqual(guia.indice, 1)
        self.assertEqual(guia.numero_guia_operadora, 509486)
        self.assertEqual(guia.numero_guia_prestador, "00363206102545280901")
        self.assertEqual(guia.tipo, "SP/SADT")
        self.assertEqual(guia.status, "Solicitação cancelada")
        self.assertIsNone(guia.codigo_prestador_solicitante)
        self.assertIsNone(guia.nome_prestador_solicitante)
        self.assertEqual(guia.local_atendimento, "MILLENNIUM EMERGENCIAS MEDICAS LTDA")
        self.assertIsNone(guia.codigo_prestador_executante)
        self.assertIsNone(guia.nome_prestador_executante)
        self.assertIsNone(guia.senha)
        self.assertEqual(guia.data_liberacao, "2025-10-06T00:00:00")
        self.assertEqual(guia.data_realizacao, "2025-10-06T00:00:00")
        self.assertIsNone(guia.data_alta)
        self.assertEqual(guia.aguardando_documentacao, "Não")
        self.assertEqual(guia.aguardando_beneficiario, "Não")
        self.assertEqual(guia.data_inclusao, "2025-10-06T08:23:29")
        self.assertIsNone(guia.status_detalhado)

    def test_guia_beneficiario_factory(self):
        received_data = DADOS_GUIA_BENEFICIARIO
        guia = criar_guia_beneficiario(received_data[0])
        self.assertIsInstance(guia, GuiaBeneficiario)