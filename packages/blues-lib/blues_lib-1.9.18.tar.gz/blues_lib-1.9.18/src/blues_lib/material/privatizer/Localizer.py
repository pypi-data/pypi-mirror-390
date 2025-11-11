from blues_lib.material.MatHandler import MatHandler
from blues_lib.type.output.STDOut import STDOut
from blues_lib.material.privatizer.image.Downloader import Downloader
from blues_lib.material.privatizer.image.Formatter import Formatter

class Localizer(MatHandler):

  def resolve(self)->STDOut:
    self._setup()

    if not self._entities:
      raise Exception(f'{self.__class__.__name__} entities is empty')

    for entity in self._entities:
      if entity['mat_stat'] == 'invalid':
        continue

      request = {
        'rule':self._rule,
        'entity':entity,
      }
      self._handle(request)

  def _handle(self,request:dict)->bool:
    try:
      downloader = Downloader(request)
      formatter = Formatter(request)
      downloader.set_next(formatter)
      downloader.handle()
      return True
    except Exception as e:
      # must update the stats
      request['entity']['mat_stat'] = 'invalid'
      request['entity']['mat_remark'] = str(e)
      
      self._logger.warning(f'localize error: {e}')
      return False
