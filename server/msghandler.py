
import time
# from game import Game
# from player import Player
from datatypes import MsgType
import settings


class MsgHandler:

	game = None

	def __init__(self, _game):
		MsgHandler.game = _game
		self.__handlers = {}

	def regist(self, msg, handler):
		self.__handlers[msg] = handler

	def regist_all(self):
		self.regist(MsgType.csNewPlayer, on_newplayer)
		self.regist(MsgType.csJoin, on_join)
		self.regist(MsgType.csMove, on_playermove)
		self.regist(MsgType.csPing, on_ping)
		self.regist(MsgType.csEatEnegyBall, on_eat_enegy_ball)
		self.regist(MsgType.csShoot, on_shoot)
		self.regist(MsgType.csHitPlayer, on_hit_player)

	def on_msg(self, player, ws, data):
		cmd = data
		if type(data) == list:
			cmd = data[0]
		handler = self.__handlers.get(cmd)
		if handler is not None:
			handler(player, ws, data)


def on_newplayer(player, ws, args):
	name = args[1]
	seed = args[2]
	# print("on new player " + name + " " + seed)
	MsgHandler.game.new_player(name, seed, ws)


def on_join(player, ws, args):
	MsgHandler.game.join(player, ws)


def on_playermove(player, ws, args):
	timestamp = args[1]
	# simTime = time.time() * 1000 - player.network_delay_time
	dir_x = args[2]
	dir_y = args[3]
	pos_x = args[4]
	pos_y = args[5]
	vx = args[6]
	vy = args[7]
	player.setposition(pos_x, pos_y)
	player.setvelocity(vx, vy)
	player.on_move(dir_x, dir_y, timestamp)


def on_ping(player, ws, args):
	server_time = args[1]
	client_time = args[2]
	player.on_ping(server_time, client_time)


def on_eat_enegy_ball(player, ws, args):
	ballid = args[1]
	MsgHandler.game.on_eat_enegy_ball(player, ballid)


def on_shoot(player, ws, args):
	timestamp = args[1]
	x = args[2]
	y = args[3]
	dirx = args[4]
	diry = args[5]
	MsgHandler.game.on_shoot_bullet(player, timestamp, x, y, dirx, diry)


def on_hit_player(player, ws, args):
	bulletid = args[1]
	playerid = args[2]
	bullet = MsgHandler.game.get_bullet(bulletid)
	if bullet is None:
		return
	player = MsgHandler.game.get_player(playerid)
	if player is None:
		return
	bullet.is_dead = True
	hurt = -settings.BULLET_DAMAGE_ENEGY
	player.add_enegy(hurt)
	MsgHandler.game.send_all(MsgType.scEnegyChange, playerid, hurt)
	MsgHandler.game.send_all(MsgType.scHitPlayer, bulletid, playerid, hurt)
	pass
