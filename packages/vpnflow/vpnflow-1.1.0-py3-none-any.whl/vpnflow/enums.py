# -*- coding: utf-8 -*-
from enum import Enum

BotCommands = Enum("BotCommands", ("start", "pay", "help", "ref"))
BotCommandsAdmin = Enum("BotCommandsAdmin", ("panel", ))
