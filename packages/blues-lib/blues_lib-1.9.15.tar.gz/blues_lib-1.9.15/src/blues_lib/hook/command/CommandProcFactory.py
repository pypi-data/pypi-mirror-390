from blues_lib.hook.ProcFactory import ProcFactory
from .processor.Skipper import Skipper
from .processor.Blocker import Blocker

class CommandProcFactory(ProcFactory):
  
  _PROC_CLASSES = {
    Skipper.__name__: Skipper,
    Blocker.__name__: Blocker,
  }