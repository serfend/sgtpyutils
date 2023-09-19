<p align="center">
    <a href="https://visitorbadge.io/status?path=https%3A%2F%2Fgithub.com%2Fserfend%2Fsgtpyutils%2F"><img src="https://api.visitorbadge.io/api/visitors?path=https%3A%2F%2Fgithub.com%2Fserfend%2Fsgtpyutils%2F&labelColor=%23697689&countColor=%23ff8a65&style=plastic&labelStyle=none" /></a> 
    <a href="https://pypi.python.org/pypi/sgtpyutils/"><img alt="pypi version" src="https://img.shields.io/pypi/v/sgtpyutils.svg" /></a> 
    <a href="https://pypistats.org/packages/sgtpyutils"><img alt="pypi download" src="https://img.shields.io/pypi/dm/sgtpyutils.svg" /></a>
    <a href="https://github.com/serfend/sgtpyutils/releases"><img alt="GitHub release" src="https://img.shields.io/github/release/serfend/sgtpyutils.svg?style=flat-square" /></a>
    <a href="https://github.com/serfend/sgtpyutils/releases"><img alt="GitHub All Releases" src="https://img.shields.io/github/downloads/serfend/sgtpyutils/total.svg?style=flat-square&color=%2364ff82" /></a>
    <a href="https://github.com/serfend/sgtpyutils/commits"><img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/serfend/sgtpyutils.svg?style=flat-square" /></a>
    <a href="https://github.com/serfend/sgtpyutils/actions/workflows/pytest.yml"><img alt="GitHub Workflow Status" src="https://github.com/serfend/sgtpyutils/actions/workflows/pytest.yml/badge.svg" /></a>
</p>




![Windows](https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)![Kali](https://img.shields.io/badge/Kali-268BEE?style=for-the-badge&logo=kalilinux&logoColor=white)![FreeBSD](https://img.shields.io/badge/-FreeBSD-%23870000?style=for-the-badge&logo=freebsd&logoColor=white)![Deepin](https://img.shields.io/badge/Deepin-007CFF?style=for-the-badge&logo=deepin&logoColor=white)![Debian](https://img.shields.io/badge/Debian-D70A53?style=for-the-badge&logo=debian&logoColor=white)![Cent OS](https://img.shields.io/badge/cent%20os-002260?style=for-the-badge&logo=centos&logoColor=F0F0F0)

# What?

sgtpyutils is python module for common utils.



## Install

```shell
pip install sgtpyutils
```



## Usage

### 日志处理
```python
from sgtpyutils.logger import logger
logger.debug('调试')
logger.info('信息')
logger.warning('警告')
```

### 时间处理
```python
from sgtpyutils.datetime import DateTime
# 当前时间
print(DateTime()) # 2023-09-19 14:50:43.570560+08:00
# 指定日期
print(DateTime('2023-09-19')) # 2023-09-19 00:00:00+08:00
# 指定时间
print(DateTime('2023-09-19 14:50:43')) # 2023-09-19 14:50:43+08:00
# 指定时间戳
print(DateTime(1695106243000)) # 2023-09-19 14:50:43+08:00
# 指定时间及时区
print(DateTime('2023-09-19T14:50:43+07:00')) # 2023-09-19 14:50:43+07:00

# 计算时间差
print((DateTime('2023-09-20') - '2023-09-19').total_seconds()) # 86400.0
print((DateTime('2023-09-20') - 60 * 1000)) # 2023-09-19 23:59:00+08:00

# 获取相对时间
print(DateTime('2023-09-20').toRelativeTime('2023-09-20 14:23')) # 14小时前
print(DateTime('2023-09-20 10:00:00').toRelativeTime('2023-09-20 10:01:00')) # 1分钟后
print(DateTime('2023-01-20 10:00:00').toRelativeTime()) # xxx年前
```





## Status

![Alt](https://repobeats.axiom.co/api/embed/af8eefa7ce843f622f7dafbfe1879a36f872474d.svg "Repobeats analytics image")
