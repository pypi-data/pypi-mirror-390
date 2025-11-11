from blues_lib.hook.command.CommandProc import CommandProc
from blues_lib.material.privatizer.Localizer import Localizer

class MatLocalizer(CommandProc):
  
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
    handler = Localizer(request)
    handler.handle()
 