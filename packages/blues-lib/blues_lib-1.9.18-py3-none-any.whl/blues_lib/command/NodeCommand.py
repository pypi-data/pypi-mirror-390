from abc import abstractmethod
from typing import final

from blues_lib.type.executor.Command import Command
from blues_lib.namespace.CommandName import CommandName
from blues_lib.namespace.CrawlerName import CrawlerName
from blues_lib.type.output.STDOut import STDOut
from blues_lib.type.model.Model import Model
from blues_lib.command.io.InputHandler import InputHandler
from blues_lib.command.io.OutputHandler import OutputHandler
from blues_lib.hook.command.CommandHook import CommandHook

class NodeCommand(Command):

  NAME = CommandName.Exception.UNSET # should be rewrite by the subclass
  TYPE = CommandName.Type.ACTION

  INPUT = CommandName.IO.INPUT
  OUTPUT = CommandName.IO.OUTPUT 
  
  def __init__(self,task_def:dict,ti:any) -> None:
    f'''
    Args:
      task_def {dict}: the task's definition
        - id {str} : the task id
        - command {str} : the command name
        - meta {dict} : the task meta data
        - bizdata {dict|None} : the task bizdata
        - input {list|dict|None} : the task input definition
        - output {list|dict|None} : the task output definition
        - setup {list|dict|None} : the task setup hook
        - teardown {list|dict|None} : the task teardown hook
      ti {any} : the task instance
    '''
    super().__init__({})
    self._task_def:dict = task_def
    self._ti:any = ti

    # init model, it will be recalculated by the InputHandler

  @property
  def id(self)->str:
    return self._task_def.get('id')

  @final
  def execute(self):
    
    InputHandler(self._task_def,self._ti).handle()
    
    # set fields after recalculate the model
    self._setup()

    # Airflow不能识别自定义异常，使用xcom标识状态
    hook_defs:list[dict] = self._task_def.get('before_invoked')
    options:dict = {'ti':self._ti}
    CommandHook(hook_defs,options).execute()
    # 因为有多个hook，所以不能基于某个实例判断是否block或skip
    CommandHook.block(self._ti)
    if CommandHook.skip(self._ti):
      self._teardown()
      return

    stdout:STDOut|dict = self._invoke() or {}
    # all ouput will be push to the xcom
    result:dict = stdout.to_dict() if isinstance(stdout,STDOut) else stdout

    hook_defs:list[dict] = self._task_def.get('after_invoked')
    options:dict = {'ti':self._ti,'result':result}
    CommandHook(hook_defs,options).execute()
    # 因为有多个hook，所以不能基于某个实例判断是否block或skip
    CommandHook.block(self._ti)
    
    # output after hook deal
    OutputHandler(self._ti,result).handle()
    self._teardown()
    
  def _setup(self): 
    
    # must crate the model after handle the input
    meta = self._task_def.get('meta') or {}
    bizdata = self._task_def.get('bizdata') or {}
    self._model:Model = Model(meta,bizdata)
    
    # recalculate the hooks' defs
    self._task_def['before_invoked'] = self._get_hook_defs('before_invoked',bizdata)
    self._task_def['after_invoked'] = self._get_hook_defs('after_invoked',bizdata)

    self._summary:dict = self._model.config.get(CrawlerName.Field.SUMMARY.value) or {}
    self._onerror:str = self._summary.get('onerror',CommandName.Exception.ABORT.value)
    
  def _get_hook_defs(self,hook_name:str,bizdata:dict)->list[dict]:
    if hook_defs:=self._task_def.get(hook_name):
      return Model(hook_defs,bizdata).config
    return []

  @abstractmethod
  def _invoke(self):
    pass

  def _teardown(self):
    code:int = self._ti.xcom_pull(key='code')
    message:str = self._ti.xcom_pull(key='message')
    if code == 200:
      self._logger.info(message)
    else:
      self._logger.error(message)
