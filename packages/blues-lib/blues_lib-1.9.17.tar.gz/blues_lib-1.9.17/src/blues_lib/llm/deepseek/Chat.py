from blues_lib.type.output.STDOut import STDOut
from .Completion import Completion

class Chat(Completion):
  _STREAM = False
  
  def _get_content(self,response)->STDOut:
    if not response.choices or not response.choices[0].message.content:
      return STDOut(
        400,
        'no content',
        None,
        response.usage,
      )

    return self._get_output(response)

  def _get_output(self,response)->STDOut:
    content:str = response.choices[0].message.content
    return STDOut(
      200,
      'success',
      content,
      response.usage,
    )

