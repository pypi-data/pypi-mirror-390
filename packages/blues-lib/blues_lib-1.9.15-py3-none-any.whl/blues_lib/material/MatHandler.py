from blues_lib.type.chain.AllMatchHandler import AllMatchHandler
from blues_lib.type.output.STDOut import STDOut

class MatHandler(AllMatchHandler):
  
  def _setup(self):
    self._entities:list[dict] = self._request.get('entities')
    if not self._entities:
      message = f'[{self.__class__.__name__}] Received an empty entity'
      raise Exception(message)

    self._rule:dict = self._request.get('rule')
    if not self._rule:
      message = f'[{self.__class__.__name__}] Received an empty rule'
      raise Exception(message)

  def _log(self,stdout:STDOut):
    if stdout.code==200:
      message = f'[{self.__class__.__name__}] Managed to retain {len(stdout.data)} entities'
      self._logger.info(message)
    else:
      message = f'[{self.__class__.__name__}] Failed to retain any valid entities - {stdout.message}'
      self._logger.error(message)
