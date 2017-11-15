import logging
import json
logging.basicConfig(level=logging.INFO)

log = logging.getLogger("psps")
from loginmanager import LoginManager
from pagemanager import PageManager 
from user import User
from page import Page

l = LoginManager()
l.load("config/users.xml")

p = PageManager()
p.load("config/pages.xml")

from multiprocessing import Process, Manager, Value
v = Value(PageManager)

print p
