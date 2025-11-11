from blues_lib.material.MatHandler import MatHandler
from blues_lib.type.output.STDOut import STDOut
from blues_lib.util.BluesURL import BluesURL
from blues_lib.util.BluesAlgorithm import BluesAlgorithm

class Normalizer(MatHandler):

  def resolve(self)->STDOut:
    self._setup()

    if not self._entities:
      raise Exception(f'{self.__class__.__name__} entities is empty')

    for entity in self._entities:

      if(entity['mat_stat'] == 'invalid'):
        continue
        
      self._add_system_fileds(entity)
      # set for detail only
      paras:list[dict] = entity.get('mat_paras')
      if paras:
        entity['mat_paras'] = self._get_format_paras(paras)
        # 如果没有缩略图，则从第一个段落中提取
        self._add_thumb(entity)
        
      # 如果没有thumb图片标识为错误 (目前用于成品判断，必须有图片)
      if not entity.get('mat_thumb'):
        entity['mat_stat'] = 'invalid'
        entity['mat_remark'] = 'no thumb image'
      
    return STDOut(200,'ok',self._entities)
  
  def _add_system_fileds(self,entity:dict):
    entity.setdefault('mat_chan',self._rule.get('mat_chan') or 'article')  # article gallery shortvideo qa
    entity.setdefault('mat_lang',self._rule.get('mat_lang') or 'cn') # cn en
    if mat_url := entity.get('mat_url'):
      mat_site = BluesURL.get_main_domain(mat_url)
      mat_id = BluesAlgorithm.md5(mat_url)
      entity.setdefault('mat_site',mat_site)  # cn en
      entity.setdefault('mat_id',mat_id) 
      
  def _add_thumb(self,entity:dict):
    if not entity.get('mat_thumb'):
      for para in entity['mat_paras']:
        if para.get('type') == 'image':
          entity['mat_thumb'] = para['value']
          break

  def _get_format_paras(self,paras:list[dict])->list[dict]:
    
    # 如果是llm获取的就是结构化数组无需转换
    if paras[0].get('type'):
      return paras

    format_paras:list[dict] = []
    for row in paras:
      image = row.get('image')
      text = row.get('text')
      if image:
        format_paras.append({'type':'image','value':image})
      else:
        format_paras.append({'type':'text','value':text})
    return format_paras

