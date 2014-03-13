import os
from logging import getLogger

logger = getLogger('lib:re:wired')
for module in os.listdir(os.path.dirname(__file__)):
    if module == '__init__.py' or module[-3:] != '.py':
        continue
    try:
        __import__(module[:-3], locals(), globals())
        logger.info("Imported " + str(module[:-3]))
    except Exception as e:
        logger.error("Failed to import %s: %s" % (module[:-3], e))
del module
