from sgtpyutils.logger import logger


def test_main():
    logger.debug('test')
    logger.info('test')
    logger.warning('test')
    logger.fatal('test')
    logger.error('test')
