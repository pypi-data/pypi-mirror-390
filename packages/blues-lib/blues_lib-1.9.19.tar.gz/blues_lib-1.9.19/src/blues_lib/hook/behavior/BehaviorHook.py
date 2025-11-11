from typing import Type
from blues_lib.hook.Hook import Hook
from .BehaviorFactory import BehaviorFactory
from .BehaviorFuncHandler import BehaviorFuncHandler

class BehaviorHook(Hook):
  
  def _get_proc_factory(self)->Type[BehaviorFactory]:
    return BehaviorFactory
  
  def _get_func_handler(self)->Type[BehaviorFuncHandler]:
    return BehaviorFuncHandler
  
  def execute(self)->any:
    '''
    @description: calculate the value in multi hooks
      The first hook's output as the next hook's input
      The result will set to the value
    '''
    if not self._hook_defs:
      return

    for hook_def in self._hook_defs:
      self._run(hook_def)

