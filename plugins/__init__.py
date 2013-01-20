import os
from logging import getLogger

logger = getLogger('lib:re:wired')
for module in os.listdir(os.path.dirname(__file__)):
    if module == '__init__.py' or module[-3:] != '.py':
        continue
    try:
        __import__(module[:-3], locals(), globals())
        logger.info("Imported " + str(module[:-3]))
    except:
        logger.error("Failed to import " + str(module[:-3]))
del module
