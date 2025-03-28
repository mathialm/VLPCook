import importlib
from bootstrap.lib.options import Options
from bootstrap.lib.logger import Logger
from bootstrap.engines.engine import Engine
from bootstrap.engines.logger import LoggerEngine


def factory():
    Logger()('Creating engine...')

    if Options()['engine'].get('import', False):
        # import usually is "yourmodule.engine.factory"
        module = importlib.import_module(Options()['engine']['import'])
        engine = module.factory()

    elif Options()['engine']['name'] == 'default':
        engine = Engine()

    elif Options()['engine']['name'] == 'logger':
        engine = LoggerEngine()

    else:
        raise ValueError

    return engine
