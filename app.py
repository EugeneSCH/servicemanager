import json
import time
import logging
from aiohttp import web
import aiohttp_jinja2
import jinja2
from aiofile import async_open
from pathlib import Path
from logging.handlers import SysLogHandler
from logging.handlers import TimedRotatingFileHandler
import os

from servicemanager import (FedoraServiceManager, AbstractServiceManager)
import settings

routes = web.RouteTableDef()


@routes.get('/')
async def root(request):
    unit: AbstractServiceManager = request.app['unit']
    unit_name, unit_status = unit.status()
    context = {'name': unit_name, 'status': unit_status}
    response = aiohttp_jinja2.render_template('tmpl.jinja2',
                                              request,
                                              context)
    return response


@routes.post('/start')
async def handler_start(request):
    unit: AbstractServiceManager = request.app['unit']
    await unit.start()
    unit_name, unit_status = unit.status()
    data = {'name': unit_name, 'status': unit_status}
    logging.info(f'Start: {data}')

    return web.json_response(data)


@routes.post('/stop')
async def handler_stopt(request):
    unit: AbstractServiceManager = request.app['unit']
    await unit.stop()
    unit_name, unit_status = unit.status()
    data = {'name': unit_name, 'status': unit_status}
    logging.info(f'Stop: {data}')

    return web.json_response(data)


@routes.post('/restart')
async def handler_restart(request):
    unit: AbstractServiceManager = request.app['unit']
    await unit.restart()
    unit_name, unit_status = unit.status()
    data = {'name': unit_name, 'status': unit_status}
    logging.info(f'Restart: {data}')

    return web.json_response(data)


@routes.post('/status')
async def handler_status(request):
    unit: AbstractServiceManager = request.app['unit']
    unit_name, unit_status = unit.status()
    try:
        async with async_open(settings.DATA_FILE_NAME, 'r') as afp:
            tmp_data = json.loads(await afp.read())
    except:
        tmp_data = {'value': False}
    data = {'name': unit_name, 'status': unit_status,
            'enabled': tmp_data.get('value')}

    return web.json_response(data)


@routes.post('/save')
async def handler_save(request):

    data = await request.json()
    logging.info(f'Save data: {data}')

    async with async_open(settings.DATA_FILE_NAME, 'w') as afp:
        await afp.write(json.dumps(data))

    return web.json_response(data)


def setup_logging(level=logging.INFO, filename=None):

    log_formatter = '%(asctime)s %(module)s [%(lineno)s] %(levelname)s : %(message)s'
    dir_name = os.path.dirname(filename)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    handler1 = TimedRotatingFileHandler(
        filename=filename, when='midnight', backupCount=5)
    handler2 = SysLogHandler(address='/dev/log')
    log_formatter2 = logging.Formatter('%(levelname)s %(module)s: %(message)s')
    handler2.setFormatter(log_formatter2)
    handler2.setLevel(logging.INFO)
    handlers = [handler1, handler2]

    if level == logging.DEBUG:
        handlers.append(logging.StreamHandler())

    logging.basicConfig(level=level, format=log_formatter, handlers=handlers)


async def on_startup(app):
    logging.info('on_startup')
    unit = FedoraServiceManager(settings.SERVICE_NAME)
    await unit.setup()
    app['unit'] = unit


async def on_shutdown(app):
    logging.info('on_shutdown')
    unit: AbstractServiceManager = app['unit']
    unit.running = False


def setup_app():
    setup_logging(settings.LOG_LEVEL, Path(
        settings.LOG_DIR).joinpath(settings.LOG_FILE_NAME))
    app = web.Application()
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    aiohttp_jinja2.setup(app,
                         loader=jinja2.FileSystemLoader(settings.TEMPLATE_FOLDER))
    app.add_routes(routes)
    return app


if __name__ == "__main__":
    app = setup_app()
    web.run_app(app)
