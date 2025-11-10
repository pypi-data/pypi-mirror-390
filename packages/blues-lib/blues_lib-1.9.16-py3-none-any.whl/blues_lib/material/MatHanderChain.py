from blues_lib.type.chain.AllMatchHandler import AllMatchHandler
from blues_lib.type.output.STDOut import STDOut
from blues_lib.material.deduplicator.Deduplicator import Deduplicator
from blues_lib.material.validator.Validator import Validator
from blues_lib.material.normalizer.Normalizer import Normalizer
from blues_lib.material.sinker.Sinker import Sinker

class MatHanderChain(AllMatchHandler):
  
  def resolve(self)->STDOut:
    try:
      chain = self._get_chain()
      stdout = chain.handle()
      # parse the request entities
      if stdout.code!=200:
        return stdout
      else:
        return STDOut(200,'ok',self._request['entities'])
    except Exception as e:
      message = f'[{self.__class__.__name__}] Failed to format - {e}'
      self._logger.error(message)
      return STDOut(500,message)
  
  def _get_chain(self)->AllMatchHandler:
    deduplicator = Deduplicator(self._request)
    validator = Validator(self._request)
    normalizer = Normalizer(self._request)
    sinker = Sinker(self._request)
    
    deduplicator.set_next(validator).set_next(normalizer).set_next(sinker)
    return deduplicator
