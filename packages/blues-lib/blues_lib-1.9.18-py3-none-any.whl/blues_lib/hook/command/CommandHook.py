from typing import Type
from blues_lib.hook.Hook import Hook
from .CommandProcFactory import CommandProcFactory
from .CommandFuncHandler import CommandFuncHandler

class CommandHook(Hook):
  
  def _get_proc_factory(self)->Type[CommandProcFactory]:
    return CommandProcFactory
  
  def _get_func_handler(self)->Type[CommandFuncHandler]:
    return CommandFuncHandler
  
  def execute(self)->None:
    if not self._hook_defs:
      return

    ti = self._options.get('ti')
    for hook_def in self._hook_defs:
      # if one hook block or skip, then break
      if ti.xcom_pull(key='should_skip') or ti.xcom_pull(key='should_block'):
        break
      self._run(hook_def)

  @classmethod
  def block(cls,ti:any)->None:
    if ti.xcom_pull(key='should_block'):
      ti.xcom_push('code',500)
      ti.xcom_push('message',f'The task {ti.task_id} is blocked')
      ti.xcom_push('data',False)
      raise Exception(f'The task {ti.task_id} is blocked')
    
  @classmethod
  def skip(cls,ti:any)->bool:
    if ti.xcom_pull(key='should_skip'):
      ti.xcom_push('code',200)
      ti.xcom_push('message',f'The task {ti.task_id} is skipped')
      ti.xcom_push('data',True)
      return True
    return False
    
