"""Strict JSON interfaces used for every model role."""
def obj(properties):
    return {'type':'object','properties':properties,'required':list(properties),'additionalProperties':False}

STRING = {'type':'string'}
STRINGS = {'type':'array','items':STRING}
OP = {'type':'string','enum':['read','write','delete','send','transform','create','finish']}
PERMISSION = obj({'op':OP,'resource':STRING,'status':{'type':'string','enum':['REQUIRED','PERMITTED','FORBIDDEN','UNRESOLVED']},'sources':STRINGS,'fields':STRINGS,'evidence':STRING})
CONTRACT = obj({'permissions':{'type':'array','items':PERMISSION}})
NODE = obj({'id':STRING,'op':OP,'resource':STRING,'sources':STRINGS,'fields':STRINGS,
            'condition':{'type':'string','enum':['always','false','unknown']},'file':STRING,'evidence':STRING})
EDGE = obj({'source':STRING,'target':STRING,'kind':{'type':'string','enum':['data','control','call','return']}})
GRAPH = obj({'nodes':{'type':'array','items':NODE},'edges':{'type':'array','items':EDGE}})
SCAN = obj({'risk':{'type':'boolean'},'reason':STRING,'evidence':STRINGS})
ACTION = obj({'op':OP,'resource':STRING,'handles':STRINGS,'fields':STRINGS,'value_json':STRING})
PLAN = obj({'actions':{'type':'array','items':ACTION},'explanation':STRING})
