from abc import abstractmethod

class HookProc():
  
  @abstractmethod
  def execute(self)->None:
    pass