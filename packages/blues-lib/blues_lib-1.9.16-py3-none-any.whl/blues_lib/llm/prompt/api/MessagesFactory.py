from .ArticleRevision import ArticleRevision
from .HtmlArticleExtractor import HtmlArticleExtractor
from .HtmlBriefExtractor import HtmlBriefExtractor
from .HtmlUrlExtractor import HtmlUrlExtractor
from .HtmlArticleRevision import HtmlArticleRevision

class MessagesFactory:
  
  _TEMPLATES:dict = {
    # 基于规范文章重写
    'ArticleRevision':ArticleRevision,
    # 基于HTML文章提取
    'HtmlArticleExtractor':HtmlArticleExtractor,
    # 基于HTML文章摘要提取
    'HtmlBriefExtractor':HtmlBriefExtractor,
    # 基于HTML文章详情页链接提取
    'HtmlUrlExtractor':HtmlUrlExtractor,
    # 基于HTML文章重写
    'HtmlArticleRevision':HtmlArticleRevision,
  }

  def __init__(self,system_prompt_topic:str) -> None:
    self._prompt = self._TEMPLATES.get(system_prompt_topic)
    if self._prompt is None:
      raise ValueError(f"topic {system_prompt_topic} not found")
  
  def create_system(self)->str:
    return self._prompt.SYSTEM
  
  def create_user(self,user_prompt:str) -> str:
    return f"{self._prompt.USER_PREFIX}{user_prompt}{self._prompt.USER_SUFFIX}"
  
  def create(self,user_prompt:str) -> list[dict[str,str]]:
    # 单轮标准对话输入
    return [
      {
        "role": "system",
        "content": self.create_system(),
      },
      {
        "role": "user",
        "content": self.create_user(user_prompt),
      },
    ]
  