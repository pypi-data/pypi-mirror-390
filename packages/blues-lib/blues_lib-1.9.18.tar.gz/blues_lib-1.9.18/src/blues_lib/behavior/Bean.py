from blues_lib.type.output.STDOut import STDOut
from blues_lib.type.executor.Behavior import Behavior
from blues_lib.hook.behavior.BehaviorHook import BehaviorHook

class Bean(Behavior):

  def _invoke(self)->STDOut:
    value = None
    try:
      if self._action()=='setter':
        value = self._set()
      else:
        value = self._get()
        value = self._after_invoked(value)
      return STDOut(200,'ok',value)
    except Exception as e:
      return STDOut(500,str(e),value)

  def _get(self)->any:
    # optional
    pass

  def _set(self)->any:
    # optional
    pass

  def _action(self)->str:
    action = 'getter'
    if 'value' in self._config:
      action = 'setter'
    return action
  
  def _after_invoked(self,value:any)->any:
    # 在getter后调用，用于处理获取到的值
    hook_defs:list[dict[str,any]] = self._config.get('after_invoked')
    options = {'value':value}
    BehaviorHook(hook_defs,options).execute()
    return options.get('value')
  
  def _get_value_entity(self)->dict|None:

    key:str|None = self._config.get('key')
    value:any = self._config.get('value')

    if key:
      return {
        key:value
      }

    if isinstance(value,dict):
      return value
    
    return None
      