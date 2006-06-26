# This file is part of Fail2Ban.
#
# Fail2Ban is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Fail2Ban is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Fail2Ban; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

# Author: Cyril Jaquier
# 
# $Revision: 1.1 $

__author__ = "Cyril Jaquier"
__version__ = "$Revision: 1.1 $"
__date__ = "$Date: 2004/10/10 13:33:40 $"
__copyright__ = "Copyright (c) 2004 Cyril Jaquier"
__license__ = "GPL"

from ssocket import SSocket
import re, pickle, logging

# Gets the instance of the logger.
logSys = logging.getLogger("fail2ban.comm")

class Transmitter:
	
	def __init__(self, server):
		self.server = server
		self.socket = SSocket(self)
	
	def start(self):
		self.socket.initialize()
		self.socket.start()
	
	##
	# Stop the transmitter.
	#
	# @bug Fix the issue with join(). When using servertestcase.py, errors
	# happen which disappear when using join() in this function.
	
	def stop(self):
		self.socket.stop()
		#self.socket.join()
		
	def proceed(self, action):
		# Deserialize object
		logSys.debug("Action: " + `action`)
		try:
			ret = self.actionHandler(action)
			ack = 0, ret
		except Exception, e:
			logSys.warn("Invalid command")
			ack = 1, e
		return ack
	
	##
	# Handle an action.
	#
	# 
	
	def actionHandler(self, action):
		if action[0] == "ping":
			return "pong"
		elif action[0] == "add":
			name = action[1]
			self.server.addJail(name)
			return name
		elif action[0] == "start":
			name = action[1]
			self.server.startJail(name)
			return None
		elif action[0] == "stop":
			name = action[1]
			self.server.stopJail(name)
			return None
		elif action[0] == "sleep":
			value = action[1]
			time.sleep(int(value))
			return None
		elif action[0] == "set":
			return self.actionSet(action[1:])
		elif action[0] == "get":
			return self.actionGet(action[1:])
		elif action[0] == "status":
			return self.status(action[1:])
		elif action[0] == "quit":
			self.server.quit()
			return None
		raise Exception("Invalid command")
	
	def actionSet(self, action):
		name = action[0]
		# Logging
		if name == "loglevel":
			value = int(action[1])
			self.server.setLogLevel(value)
			return self.server.getLogLevel()
		# Jail
		if action[1] == "idle":
			if action[2] == "on":
				self.server.setIdleJail(name, True)
			elif action[2] == "off":
				self.server.setIdleJail(name, False)
			return self.server.getIdleJail(name)
		# Filter
		elif action[1] == "logpath":
			value = action[2]
			self.server.setLogPath(name, value)
			return self.server.getLogPath(name)
		elif action[1] == "timeregex":
			value = action[2]
			self.server.setTimeRegex(name, value)
			return self.server.getTimeRegex(name)
		elif action[1] == "timepattern":
			value = action[2]
			self.server.setTimePattern(name, value)
			return self.server.getTimePattern(name)
		elif action[1] == "failregex":
			value = action[2]
			self.server.setFailRegex(name, value)
			return self.server.getFailRegex(name)
		elif action[1] == "maxtime":
			value = action[2]
			self.server.setMaxTime(name, int(value))
			return self.server.getMaxTime(name)
		elif action[1] == "maxretry":
			value = action[2]
			self.server.setMaxRetry(name, int(value))
			return self.server.getMaxRetry(name)
		# Action
		elif action[1] == "bantime":
			value = action[2]
			self.server.setBanTime(name, int(value))
			return self.server.getBanTime(name)
		elif action[1] == "actionstart":
			value = action[2]
			self.server.setActionStart(name, value)
			return self.server.getActionStart(name)
		elif action[1] == "actionstop":
			value = action[2]
			self.server.setActionStop(name, value)
			return self.server.getActionStop(name)
		elif action[1] == "actioncheck":
			value = action[2]
			self.server.setActionCheck(name, value)
			return self.server.getActionCheck(name)
		elif action[1] == "actionban":
			value = action[2]
			self.server.setActionBan(name, value)
			return self.server.getActionBan(name)
		elif action[1] == "actionunban":
			value = action[2]
			self.server.setActionUnban(name, value)
			return self.server.getActionUnban(name)
		raise Exception("Invalid command (no set action)")
	
	def actionGet(self, action):
		name = action[0]
		# Logging
		if name == "loglevel":
			return self.server.getLogLevel()
		# Filter
		if action[1] == "logpath":
			return self.server.getLogPath(name)
		raise Exception("Invalid command (no get action)")
	
	def status(self, action):
		if len(action) == 0:
			return self.server.status()
		else:
			name = action[0]
			return self.server.statusJail(name)
		raise Exception("Invalid command (no status)")
	