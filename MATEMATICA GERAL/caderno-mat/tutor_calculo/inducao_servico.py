"""Artefatos de ilustração reutilizam tarefas/IDs/PNGs, sem recálculo de provas."""
from .calculos import Calculos,processo
from .inducao import VERSAO,validar_spec,resumo

class Inducao(Calculos):
    versao=VERSAO
    validar=staticmethod(validar_spec)
    resumir=staticmethod(resumo)
    processar=staticmethod(lambda s,t:processo(s,t,timeout=15,modulo='tutor_calculo.inducao'))
    modelo_local='Ilustração local · sem verificação matemática'
    def descrever(self,s):return 'Criar ilustração de indução: '+s['proposicao']+'; início '+str(s['inicio'])
    def titulo(self,s):return s['titulo']
    def executar(self,op,d):
        return super().executar({'inducao_executar':'math_executar','inducao_obter':'math_obter','inducao_cancelar':'math_cancelar'}[op],d)
