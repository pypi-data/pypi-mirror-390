from blues_lib.command.NodeCommand import NodeCommand
from blues_lib.type.output.STDOut import STDOut
from blues_lib.llm.deepseek.JsonChat import JsonChat    
from blues_lib.llm.deepseek.ChatMessages import ChatMessages
from blues_lib.namespace.CommandName import CommandName

class Writer(NodeCommand):

  NAME = CommandName.LLM.WRITER

  def _setup(self)->bool:
    super()._setup()
    self._request_body:dict = self._summary.get('request_body') # deepseek request body
    self._entities:list[dict] = self._get_entities()
    self._errors:list[str] = []
    
  def _get_entities(self)->list[dict]:
    entities:list[dict] = self._summary.get('entities') or []
    if entities:
      # 多条数据处理，且需要与扩展属性合并，必须包含 user_prompt字段
      entities = [entity for entity in entities if entity.get('user_prompt')]
    elif user_prompt:= self._summary.get('user_prompt'):
      # 单条数据处理
      entities = [{'user_prompt':user_prompt}]
    return entities

  def _invoke(self)->STDOut:
    total:list[dict] = []
    if not self._entities:
      raise ValueError(f'{self.NAME} : no entities or user_prompt')

    for entity in self._entities:
      items:list[dict] = self._invoke_one(entity['user_prompt'])
      if items:
        self._append(total,items,entity)

    if not total:
      raise ValueError(f'{self.NAME} : llm errors : {self._errors}')

    return STDOut(200,'ok',total)
  
  def _append(self,total:list[dict],items:list[dict],entity:dict):
    # 合并实体属性和llm输出属性
    for item in items:
      # llm输出优先
      merged = {**entity,**item}
      # 删除过程属性
      del merged['user_prompt']
      total.append(merged)

  def _invoke_one(self,user_prompt:str)->list[dict]|None:

    prompt_def = {**self._summary,'user_prompt':user_prompt} 
    messages = ChatMessages(prompt_def).create()
    # always get a json object list
    output:STDOut = JsonChat(self._request_body).ask(messages)
    print(f'---> llm output: {output}')
    if output.code == 200 and output.data:
      # 确保输出是数组格式，llm输出有可能是单条数据
      return output.data if isinstance(output.data,list) else [output.data]
    else:
      raise None

    