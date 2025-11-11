from blues_lib.util.html.HtmlExtractor import HtmlExtractor 
from blues_lib.hook.behavior.BehaviorProc import BehaviorProc

class HtmlFilter(BehaviorProc):
  
  def execute(self)->list[dict]|None:
    '''
    @description: convert the answer to mat dict
    @return {list[dict]|None} the mat dict list
    '''
    if value:=self._options.get('value'):
      includes:list[str] = self._proc_conf.get('includes',[]) 
      excludes:list[str] = self._proc_conf.get('excludes',[])
      result:dict = HtmlExtractor().extract(value, includes,excludes)
      self._options['value'] = result['html']

