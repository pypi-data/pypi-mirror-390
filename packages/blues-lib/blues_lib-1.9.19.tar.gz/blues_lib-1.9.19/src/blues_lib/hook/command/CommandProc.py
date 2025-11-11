from blues_lib.hook.HookProc import HookProc

class CommandProc(HookProc):
  
  def __init__(self,proc_def:dict,options:dict) -> None:
    self._proc_conf = proc_def
    self._ti = options.get('ti')
    self._result = options.get('result',{})
