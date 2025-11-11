from blues_lib.material.MatHandler import MatHandler
from blues_lib.dao.material.MatQuerier import MatQuerier
from blues_lib.type.output.STDOut import STDOut

class Deduplicator(MatHandler):

  def resolve(self)->STDOut:
    self._setup()
    
    if not self._entities:
      raise Exception(f'{self.__class__.__name__} entities is empty')

    avail_entities = []
    unavail_entities = []

    querier = MatQuerier()
    key = self._rule.get('key','url')
    field = self._rule.get('field','mat_url')

    for entity in self._entities:
      if not entity.get(key):
        unavail_entities.append(entity)
        continue

      if querier.exist(entity[key],field):
        unavail_entities.append(entity)
        continue

      avail_entities.append(entity)

    if avail_entities:
      return STDOut(200,'ok',avail_entities,unavail_entities)
    else:
      return STDOut(500,'all brief urls are duplicated')
