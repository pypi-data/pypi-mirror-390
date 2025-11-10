from blues_lib.llm.prompt.template.html.DetailExtractor import DetailExtractor
from blues_lib.llm.prompt.template.html.DetailRevision import DetailRevision
from blues_lib.llm.prompt.template.html.BriefExtractor import BriefExtractor
from blues_lib.llm.prompt.template.revision.ArticleRevision import ArticleRevision

class PromptFactory:
  
  templates:dict = {
    # HTML文章详情提取
    'DetailExtractor':DetailExtractor.MARKDOWN,
    # HTML文章摘要提取
    'BriefExtractor':BriefExtractor.MARKDOWN,
    # 基于HTML文章重写
    'DetailRevision':DetailRevision.MARKDOWN,
    # 基于规范文章重写
    'ArticleRevision':ArticleRevision.MARKDOWN,
  }
  
  def create(self,topic:str,text:str)->dict:
    prompt:dict = self.templates.get(topic)
    if not prompt:
      raise ValueError(f'Prompt topic {topic} not found')
    return f'{prompt}{text}'
