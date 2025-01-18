from sgtpyutils.network.httpx import get_url
import asyncio
def test_baidu():
  data = asyncio.run(get_url('https://baidu.com'))
  assert len(data)
  assert 'baidu' in data
