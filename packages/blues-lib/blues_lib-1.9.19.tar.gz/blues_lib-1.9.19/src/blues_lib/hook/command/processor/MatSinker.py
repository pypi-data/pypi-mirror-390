from blues_lib.hook.command.CommandProc import CommandProc
from blues_lib.material.sinker.Sinker import Sinker

class MatSinker(CommandProc):
  
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
    # 只修改状态和备注字段值，无数组长度变化
    handler = Sinker(request)
    sql_output:STDOut = handler.handle()
    if sql_output.code != 200:
      raise ValueError(f'{self.__class__.__name__} : failed to sink entities : {sql_output.message}')

    # 区分两种状态数据，非法数据单独输出
    available_entities,invalid_entities,invalid_messages = self._split_by_status(entities)
    
    # 合法数据作为标准数据
    if available_entities:
      self._result['data'] = available_entities
    else:
      raise ValueError(f'{self.__class__.__name__} : all entities are invalid : {";".join(invalid_messages)}')
    
  def _split_by_status(self,entities:list[dict])->tuple[list[dict],list[dict]]:
    available_entities:list[dict] = []
    invalid_entities:list[dict] = []
    invalid_messages:list[str] = []
    for entity in entities:
      if entity['mat_stat'] == 'available':
        available_entities.append(entity)
      else:
        invalid_entities.append(entity)
        invalid_messages.append(f"{entity['mat_title']} - {entity['mat_remark']}")
        
    return available_entities,invalid_entities,invalid_messages

 