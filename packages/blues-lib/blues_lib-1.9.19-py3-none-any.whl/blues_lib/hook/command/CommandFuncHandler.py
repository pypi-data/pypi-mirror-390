from blues_lib.hook.FuncHandler import FuncHandler

class CommandFuncHandler(FuncHandler):
  
  def execute(self)->any:
    ti:any = self._options.get('ti')
    result:dict = self._options.get('result',{})
    self._func(ti,result)
