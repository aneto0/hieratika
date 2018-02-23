from hieratikaclient import HieratikaClient
import logging
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] [%(process)d] [%(thread)d] [%(filename)s:%(lineno)d] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

hc = HieratikaClient("192.168.130.46")
hc.login("gcc-configurator", "")
print hc.getUser()
scheduleFolders = hc.getScheduleFolders("gcc-configurator", "GCC", [])
print scheduleFolders
schedules = hc.getSchedules("gcc-configurator", "GCC", ["Campaigns"])
print schedules
hc.logout()


