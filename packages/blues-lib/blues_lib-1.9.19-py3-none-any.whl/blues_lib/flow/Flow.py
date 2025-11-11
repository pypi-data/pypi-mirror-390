from blues_lib.type.executor.Executor import Executor
from blues_lib.type.output.STDOut import STDOut
from blues_lib.util.BluesMailer import BluesMailer  
from blues_lib.flow.MockTI import MockTI

class Flow(Executor):
  
  def __init__(self): 
    super().__init__()
    self._executors:list[Executor] = []
    self._task_ids:list[str] = []
    
  def get_task_result(self,task_id:str)->dict:
    return self.ti_store.get(task_id) or {}
  
  def last_task_result(self)->dict:
    return self.get_task_result(self.task_ids[-1])
    
  @property
  def ti_store(self)->dict:
    # it's static field
    return MockTI.store

  @property
  def size(self)->int:
    return len(self._executors)

  @property
  def task_ids(self)->list[str]:
    return self._task_ids
    
  @property
  def executors(self)->list[Executor]:
    return self._executors
    
  def add(self,executor:Executor):
    self._executors.append(executor)

  def execute(self)->STDOut:
    if not self._executors:
      return STDOut(404,'No executors to execute the flow')

    for executor in self._executors:
      self._logger.info(f'Task {executor.id} started')
      self._task_ids.append(executor.id)
      try:
        executor.execute()
      except Exception as e:
        message = f'[{self.__class__.__name__}] Failed to execute the task {executor.id} - {e}'
        self._logger.error(message)
        self._send_error_mail(message)
        # break and return the flow
        return STDOut(500,message)

    return STDOut(200,f'Success to execute the flow - {"->".join(self._task_ids)}')
        
  def _send_error_mail(self,message:str):
    subject = 'Failed to execute the flow'
    paras = [{
      'type':'text',
      'value':message,
    }]
    
    payload = {
      'subject':subject,
      'paras':paras,
      'addressee':['langcai10@dingtalk.com'], # send to multi addressee
      'addressee_name':'BluesLiu',
    }
    mailer = BluesMailer.get_instance()
    return mailer.send(payload)