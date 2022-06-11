
from sgtpyutils.network.TcpClient import start_client
from sgtpyutils.logger import logger
from sgtpyutils.network.SimpleProxyProcessService import SimpleProxyProcessService
from .common import get_elf_resources

import pytest
import platform


@pytest.mark.skipif(platform.uname()[0] == 'Linux', reason='skip linux')
@pytest.mark.skipif(platform.uname()[0] == 'Darwin', reason='skip mac')
def test_process_redirect():
    # elf = get_elf_resources('pwn1')
    # s = SimpleProxyProcessService(elf)
    s = SimpleProxyProcessService(['cmd'])
    c = start_client(s.port)
    c.send(b'whoami\n')
    data = c.recv(1)
    pass
    
    
    


