from blues_lib.type.factory.Factory import Factory
from blues_lib.command.CommandFactory import CommandFactory
from blues_lib.command.NodeCommand import NodeCommand
from blues_lib.flow.Flow import Flow
from blues_lib.flow.MockTI import MockTI

class FlowFactory(Factory):
  
  def __init__(self,task_defs:list[dict]) -> None:
    self._task_defs:list[dict] = task_defs

  def create(self)->Flow | None:
    flow = Flow()
    for task_def in self._task_defs:
      self._add_command(flow,task_def)
    
    return flow if flow.size else None
  
  def _add_command(self,flow:Flow,task_def:dict):
    ti = MockTI(task_def.get('id'))
    executor:NodeCommand|None = CommandFactory().create(task_def,ti)
    if not executor:
      raise ValueError(f'Command {task_def.get("command")} is not supported')

    flow.add(executor)
