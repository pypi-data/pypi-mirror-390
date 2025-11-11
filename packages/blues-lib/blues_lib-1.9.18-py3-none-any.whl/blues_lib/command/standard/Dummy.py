from blues_lib.command.NodeCommand import NodeCommand
from blues_lib.namespace.CommandName import CommandName
from blues_lib.type.output.STDOut import STDOut

class Dummy(NodeCommand):
  
  NAME = CommandName.Standard.DUMMY

  def _invoke(self)->STDOut:
    code:int = self._summary.get('code',200)
    message:str = self._summary.get('message','ok')
    data:any = self._summary.get('data','dummy')
    detail:any = self._summary.get('detail',None)

    # just return the input params
    return STDOut(code,message,data,detail)
