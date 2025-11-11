import logging
from functools import wraps

class LogDeco():
  '''
  Only used to the Acter class's resovle method
  '''
  def __init__(self):
    '''
    Create the decorator
    Has no parameters
    '''
    pass

  def __call__(self,func):
    @wraps(func) 
    def wrapper(this,*arg,**kwargs):

      outcome = func(this,*arg,**kwargs)

      if this.message:
        logger = logging.getLogger('airflow.task')
        logger.info(this.message)
      
      return outcome

    return wrapper

