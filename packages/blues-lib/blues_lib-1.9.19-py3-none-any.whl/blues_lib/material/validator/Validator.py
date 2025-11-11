import math
from blues_lib.material.MatHandler import MatHandler
from blues_lib.type.output.STDOut import STDOut

class Validator(MatHandler):

  def resolve(self)->STDOut:
    self._setup()

    if not self._entities:
      raise Exception(f'{self.__class__.__name__} entities is empty')

    for entity in self._entities:
      has_image,error = self._has_image(entity)
      if not has_image:
        entity['mat_stat'] = 'invalid'
        entity['mat_remark'] = error
        continue

      if not self._rule:
        entity['mat_stat'] = 'available'
        continue

      is_valid,error = self._is_valid_entity(entity)
      if is_valid:
        entity['mat_stat'] = 'available'
        continue

      entity['mat_stat'] = 'invalid'
      entity['mat_remark'] = error

    return STDOut(200,'ok',self._entities)
  
  def _has_image(self,entity:dict)->tuple[bool,str]:
    paras:list[dict] = entity.get('mat_paras',[])
    if not paras:
      return (True,'not detail entity')

    for para in paras:
      if para.get('type') == 'image':
        return (True,'ok')
    return (False,'no image')
  
  def _is_valid_entity(self,entity:dict)->tuple[bool,str]:
    for field,rule in self._rule.items():
      if field not in entity:
        return (False,f"{field} is missing")

      # 如果是字典才有更多配置
      if not rule or not isinstance(rule,dict):
        continue
      
      # 只有有属性才是必填，值为对象进一步添加规则
      field_value:any = entity.get(field)

      min_length = rule.get('min_length')
      max_length = rule.get('max_length')
      field_len:int = self._get_field_length(field,field_value)

      if min_length and field_len<min_length:
        return (False,f"{field} is too short : {field_len}, at least {min_length}")

      if max_length and field_len>max_length:
        return (False,f"{field} is too long : {field_len}, at most {max_length}")

    return (True,'ok')
  
  def _get_len(self, text: str) -> int:
    """
    计算字符串长度，中文按长度1计算；英文和符号按0.5计算，结果向上取整
    """
    length = 0
    for char in text:
      # 判断是否为中文字符
      if '\u4e00' <= char <= '\u9fff':
        length += 1
      else:
        length += 0.5
    # 向上取整，确保返回整数
    return math.ceil(length)

  def _get_field_length(self,field:str,field_value:any)->int:

    if field == 'mat_paras':
      size = 0
      paras:list[str] = field_value
      for para in paras:
        p_type = para.get('type')
        p_value = para.get('value')  or '' # must be a str
        if p_type == 'text':
          size += self._get_len(p_value)
      return size
    
    return self._get_len(str(field_value))
    
    



     