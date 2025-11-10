
class ChatMessages:
  
  def __init__(self,prompt_def:dict) -> None:
    self._prompt_def = prompt_def
  
  def _get_system_message(self)->list[dict[str,str]]:
    system_prompt = self._prompt_def.get('system_prompt')
    if not system_prompt:
      return []

    return [
      {
        "role": "system",
        "content": system_prompt,
      }
    ]
  
  def _get_user_message(self) -> list[dict[str,str]]:
    user_prompt:str = self._prompt_def.get('user_prompt') or ''
    user_prefix:str = self._prompt_def.get('user_prefix') or ''
    user_suffix:str = self._prompt_def.get('user_suffix') or ''
    max_chars:int = int(self._prompt_def.get('max_chars') or 4000)

    if not user_prompt:
      raise ValueError(f'{self.NAME} : no user_prompt')

    if len(user_prompt) > max_chars:
      user_prompt = user_prompt[:max_chars]

    content:str = f"{user_prefix}{user_prompt}{user_suffix}"

    return [
      {
        "role": "user",
        "content": content,
      }
    ]
  
  def create(self) -> list[dict[str,str]]:
    system_message:list[dict[str,str]] = self._get_system_message()
    user_message:list[dict[str,str]] = self._get_user_message()
    return system_message + user_message
  