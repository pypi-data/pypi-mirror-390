from blues_lib.hook.command.CommandProc import CommandProc
from blues_lib.type.output.STDOut import STDOut
from blues_lib.material.deduplicator.Deduplicator import Deduplicator

class MatDeduplicator(CommandProc):
  
  def execute(self)->None:
    '''
    @description: block the flow
    @return: None
    '''
    rule:dict = self._proc_conf.get('rule',{})
    entities:list[dict] = self._result.get('data') or []

    request = {
      'rule':rule,
      'entities':entities, # must be a list
    } 
    # 不论是否合法都存入表，后续可以根据状态进行筛选
    handler = Deduplicator(request)
    output:STDOut = handler.handle()
    
    # just update the result
    if output.code==200 and output.data:
      self._result['data'] = output.data
      print(f'{self.__class__.__name__} : {len(output.detail)} deduplicated materials ')
    else:
      raise ValueError(f'{self.__class__.__name__} : {output.message}')
 