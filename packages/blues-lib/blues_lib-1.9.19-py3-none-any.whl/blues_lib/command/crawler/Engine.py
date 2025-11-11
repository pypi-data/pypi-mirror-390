from blues_lib.command.NodeCommand import NodeCommand
from blues_lib.type.output.STDOut import STDOut
from blues_lib.crawler.CrawlerFactory import CrawlerFactory
from blues_lib.sele.browser.chrome.ChromeFactory import ChromeFactory   
from blues_lib.namespace.CommandName import CommandName
from blues_lib.namespace.CrawlerName import CrawlerName

class Engine(NodeCommand):

  NAME = CommandName.Crawler.ENGINE

  def _invoke(self)->STDOut:
    browser = self._create_browser()
    if not browser:
      raise Exception(f'[{self.NAME}] fail to create the browser')

    browser_type:str = self._summary.get(CrawlerName.Field.TYPE.value,CrawlerName.Engine.URL.value)
    crawler_name:CrawlerName = CrawlerName.Engine.from_value(browser_type)
    crawler = CrawlerFactory(self._model,browser).create(crawler_name)
    return crawler.execute()
  
  def _create_browser(self):
    browser_conf:dict = self._summary.get('driver') or {}
    driver_config =  browser_conf.get('config') # optional
    driver_options = browser_conf.get('options') or {} # optional
    return ChromeFactory(**driver_options).create(driver_config)