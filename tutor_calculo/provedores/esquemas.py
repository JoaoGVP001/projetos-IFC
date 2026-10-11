"""Formato estruturado de estudo: restringe tipos, nunca entrega gabaritos."""


def atividade(pedido):
    text={'type':'string'}
    alternative={'type':'object','properties':{'id':text,'texto':text},'required':['id','texto'],'additionalProperties':False}
    reference={'type':'object','properties':{'material_id':text,'pagina':{'type':['integer','null']}},
               'required':['material_id','pagina'],'additionalProperties':False}
    questions=[]
    for form in pedido['formatos']:
        props={'id':text,'enunciado':text,'formato':{'type':'string','enum':[form]},'assunto':text,
               'dificuldade':{'type':'string','enum':[pedido['dificuldade']]},
               'alternativas':{'type':'array','items':alternative,'minItems':2 if form=='escolha' else 0,'maxItems':6 if form=='escolha' else 0},
               'explicacao':text,'resposta':{'type':'boolean' if form=='vf' else 'string'},
               'tolerancia':text,'referencias':{'type':'array','items':reference,'maxItems':6}}
        questions.append({'type':'object','properties':props,'required':list(props),'additionalProperties':False})
    props={k:text for k in ('titulo','descricao','assuntos','etiquetas','objetivo')}
    props['dificuldade']={'type':'string','enum':[pedido['dificuldade']]}
    props['exercicios']={'type':'array','minItems':pedido['quantidade'],'maxItems':pedido['quantidade'],
                        'items':questions[0] if len(questions)==1 else {'anyOf':questions}}
    return {'type':'object','properties':props,'required':list(props),'additionalProperties':False}
