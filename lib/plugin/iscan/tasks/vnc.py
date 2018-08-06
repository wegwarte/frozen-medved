import tempfile

from lib.exec import Task

class VNCFindTask(Task): # pylint: disable=too-few-public-methods
  """Tries to connect FTP service with various credentials"""
  def _process(self, item):
    fd, temp_path = tempfile.mkstemp()
    print(fd, temp_path)
 