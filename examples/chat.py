import asyncio
import os
import logging
from aiohttp import web

import sockjs

CHAT_FILE = open(
    os.path.join(os.path.dirname(__file__), 'chat.html'), 'rb').read()


def chat_msg_handler(msg, session):
    if msg.tp == sockjs.MSG_OPEN:
        session.manager.broadcast("Someone joined.")
    elif msg.tp == sockjs.MSG_MESSAGE:
        session.manager.broadcast(msg.data)
    elif msg.tp == sockjs.MSG_CLOSED:
        session.manager.broadcast("Someone left.")


def index(request):
    return web.Response(body=CHAT_FILE, content_type='text/html')


if __name__ == '__main__':
    """Simple sockjs chat."""
    loop = asyncio.get_event_loop()
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(message)s')

    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', index)
    sockjs.add_endpoint(app, chat_msg_handler, name='chat', prefix='/sockjs/')

    handler = app.make_handler()
    srv = loop.run_until_complete(
        loop.create_server(handler, '127.0.0.1', 8080))
    print("Server started at http://127.0.0.1:8080")
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        srv.close()
        loop.run_until_complete(handler.finish_connections())
