class OutputHandler:

  def __init__(self,ti:any,result:dict) -> None:
    self._ti = ti
    self._result = result

  def handle(self):
    if not self._result:
      return

    for key,value in self._result.items():
      self._ti.xcom_push(key,value)
