"""Sinais restritos de redação matemática; não avaliam provas nem equivalência.

Retenção conservadora dos erros observados, sem regenerar ou corrigir a prosa.
Texto que não aciona as regras continua sem certificação matemática.
"""
import re
import unicodedata


class RespostaRetida(RuntimeError):
    def __init__(self, motivo, texto, titulo, resposta):
        super().__init__(motivo)
        self.resposta=resposta
        self.metricas={'consulta_modelo':True,'qualidade':{
            'estado':'recusada','titulo':titulo,'aviso':motivo,
            'verificacao_matematica':'não realizada; somente sinais locais de revisão',
            'rascunho_recusado':texto[:12000],'rascunho_abreviado':len(texto)>12000}}


def normalizar(texto):
    return ''.join(c for c in unicodedata.normalize('NFD',texto.casefold()) if not unicodedata.combining(c))


def escopo(pergunta,modo):
    if modo not in ('Resolver','Explicar','Corrigir','Explicar cálculo','Explicar Discreta'):return []
    p=normalizar(pergunta);out=[]
    if re.search(r'\binducao\b',p):out.append('inducao')
    if modo=='Explicar cálculo' or re.search(r'\b(?:limites?|derivadas?|continuidade|tangentes?)\b|f\s*\(\s*x\s*\)',p):out.append('calculo')
    return out


def conferir(pergunta,texto,modo):
    areas=escopo(pergunta,modo)
    for linha in texto.splitlines():
        n=normalizar(linha)
        sinais=[]
        if 'inducao' in areas:
            # Regras de recusa, não critérios suficientes de validade de prova.
            m=re.search(r'\b(?:se|suponha|assuma)\b.{0,140}\bpara (?:algum|um certo)\s+(?:(?:numero\s+)?(?:inteiro|natural)\s+)?[$\\({\s]*k\b',n)
            if m:sinais.append((m,'No passo indutivo, confira se k foi escolhido arbitrariamente, em vez de um caso específico.'))
        if 'calculo' in areas:
            for pattern,msg in (
                (r'\bassintota\s+removivel\b','Um buraco com limite finito é descontinuidade removível; confira o uso de assíntota.'),
                (r'\bsimplificacao\b.{0,35}\bremove\b.{0,20}\bburaco\b','Cancelar fatores conserva o domínio original; confira a afirmação de que a simplificação remove o buraco.'),
            ):
                m=re.search(pattern,n)
                if m:sinais.append((m,msg))
        for m,msg in sinais:
            # Não recuse uma correção explicitamente negativa nem uma menção
            # marcada como erro. A heurística continua sujeita a falsos positivos.
            prefix=re.split(r'(?<=[.!?;])\s+',n[:m.start()])[-1][-100:]
            if re.search(r'\b(?:nao|incorret[oa]|errad[oa]|erro|evite)\b',prefix+n[m.start():m.end()]):continue
            if 'inducao' in areas and re.search(r'\barbitrar(?:io|iamente)\b',n[m.start():m.end()+60]):continue
            raise RespostaRetida(msg,texto,'Redação matemática retida para revisão',
                'Esta explicação foi retida por um sinal local de redação matemática que exige revisão. '
                'Confira o diagnóstico abaixo e os parâmetros nas ferramentas locais. '
                'O aplicativo não corrigiu a demonstração automaticamente nem certificou o resultado.')
    return {'escopo':areas,'sinais_encontrados':0,
            'aviso':'Não encontrar estes padrões não verifica contas, domínio, hipóteses ou demonstração.'}
