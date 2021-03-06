import os
import asyncio
import json
from aiohttp import web
import time

import settings
from game import Game
from msghandler import MsgHandler
from msgsender import MsgSender
from datatypes import MsgType


async def handle(request):
	return web.Response(status=404)

async def wshandler(request):
	print("connected")
	_game = request.app["game"]
	msghandler = request.app["msghandler"]
	ws = web.WebSocketResponse()
	await ws.prepare(request)

	player = None
	while True:
		msg = await ws.receive()
		if msg.tp == web.MsgType.text:
			# print("recv msg %s" % msg.data)
			data = json.loads(msg.data)
			if player is None and data[0] == MsgType.csNewPlayer:
				player = MsgHandler.game.new_player(data[1], data[2], ws)
			else:
				msghandler.on_msg(player, ws, data)
		elif msg.tp == web.MsgType.close:
			break

	if player:
		_game.player_disconnected(player)

	print("disconnected")
	return ws

async def game_loop(game):
	print("\n>>>>>>>>>>>>>>>>>>>")
	print("Server starts !")
	print("World size : %d x %d" % (settings.WORLD_WIDTH, settings.WORLD_HEIGHT))
	print("Max players : %d" % settings.MAX_PLAYERS)
	print("FPS : %d" % settings.GAME_SPEED)
	print("Enter looping...")

	tick = 1./settings.GAME_SPEED
	lasttick = time.clock()
	while 1:
		curtick = time.clock()
		dt = curtick - lasttick
		if dt < tick:
			await asyncio.sleep(tick - dt)
			continue
		game.update_world(dt)
		lasttick = curtick

	print("Exit looping")
	print(">>>>>>>>>>>>>>>>>>>\n")
	pass

event_loop = asyncio.get_event_loop()
event_loop.set_debug(True)

app = web.Application()

app["game"] = Game()
app["game"].create_world()
app["msghandler"] = MsgHandler(app["game"])
app["msghandler"].regist_all()
app["msgsender"] = MsgSender(app["game"])

app.router.add_route('GET', '/connect', wshandler)
# app.router.add_route('GET', '/{name}', handle)
# app.router.add_route('GET', '/', handle)

asyncio.ensure_future(game_loop(app["game"]))

port = int(os.environ.get('PORT', 5000))
web.run_app(app, host='127.0.0.1', port=port)
