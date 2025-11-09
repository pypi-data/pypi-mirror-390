from blues_lib.type.factory.Factory import Factory
from blues_lib.type.executor.Command import Command
from blues_lib.namespace.CommandName import CommandName

# standard
from blues_lib.command.standard.Dummy import Dummy
from blues_lib.command.standard.Cleaner import Cleaner

# control
from blues_lib.command.control.Blocker import Blocker
from blues_lib.command.control.Retryer import Retryer
from blues_lib.command.control.Printer import Printer

# browser
from blues_lib.command.browser.Creator import Creator

# sql
from blues_lib.command.sql.Querier import Querier
from blues_lib.command.sql.Updater import Updater
from blues_lib.command.sql.Inserter import Inserter
from blues_lib.command.sql.Deleter import Deleter

# llm
from blues_lib.command.llm.Writer import Writer

# crawler
from blues_lib.command.crawler.Engine import Engine

# material
from blues_lib.command.material.Sinker import Sinker
from blues_lib.command.material.Deduplicator import Deduplicator
from blues_lib.command.material.Validator import Validator
from blues_lib.command.material.Normalizer import Normalizer
from blues_lib.command.material.Localizer import Localizer

# notifier
from blues_lib.command.notifier.Email import Email

# --- flow command ---
# flow
from blues_lib.command.flow.Engine import Engine as FlowEngine

class CommandFactory(Factory):

  _COMMANDS:dict[str,Command] = {
    # standard
    Dummy.NAME:Dummy,
    Cleaner.NAME:Cleaner,
    
    # control
    Blocker.NAME:Blocker,
    Retryer.NAME:Retryer,
    Printer.NAME:Printer,
    
    # browser
    Creator.NAME:Creator,
    
    # llm
    Writer.NAME:Writer,
    
    # crawler
    Engine.NAME:Engine,
    
    # sql
    Querier.NAME:Querier,
    Updater.NAME:Updater,
    Inserter.NAME:Inserter,
    Deleter.NAME:Deleter,
    
    # material
    Sinker.NAME:Sinker,
    Deduplicator.NAME:Deduplicator,
    Validator.NAME:Validator,
    Normalizer.NAME:Normalizer,
    Localizer.NAME:Localizer,
    
    # notifier
    Email.NAME:Email,

    # flow command
    FlowEngine.NAME:FlowEngine,
  }
  
  _TASK_CONF_FIELDS:list[str] = [
    'id',
    'command',
    'meta',
  ]
  
  @classmethod
  def create(cls,task_def:dict,ti:any)->Command | None:
    
    error:str = cls.check(task_def,ti)
    if error:
      raise ValueError(f"Failed to create command - {error}")

    # overide
    command_value:str = task_def.get('command')
    command_name:CommandName|None = CommandName.from_value(command_value)
    if not command_name:
      error = f"The command '{command_value}' is not supported."
      raise ValueError(f"Failed to create command - {error}")

    executor:Command|None = cls._COMMANDS.get(command_name)
    if not executor:
      error = f"The command '{command_value}' is not supported."
      raise ValueError(f"Failed to create command - {error}")

    return executor(task_def,ti)
  
  @classmethod
  def check(cls,task_def:dict,ti:any)->str:
    error:str = ''
    if not ti:
      error = "The parameter 'ti' is missing."
    if not task_def:
      error = "The parameter 'task_def' is missing."

    for field in cls._TASK_CONF_FIELDS:
      if task_def.get(field) is None:
        error = f"The parameter 'task_def.{field}' is missing."   
        break
    return error

