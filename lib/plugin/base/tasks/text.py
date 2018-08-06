from lib.exec import Task
from jinja2 import Environment, FileSystemLoader


class Jinja2TemplateTask(Task):
  def __init__(self, id, root):
    super().__init__(id, root)

  def _process(self, item):
    template = Environment(loader=FileSystemLoader('.')).get_template(self.lcnf.get('path'))
    item['data']['message'] = template.render(data = item['data'])
    item['steps'][self._id] = True

  def _run(self, items):
    for item in items:
      self._process(item)
    return items
