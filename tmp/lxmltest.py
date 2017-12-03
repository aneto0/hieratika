import time
import timeit
from lxml import etree
tree = etree.parse("/home/aneto/Projects/hieratika/demo/server/psps/psps/configuration/Psps-dummy2/000/plant.xml")

xmlns = {"ns0": "http://www.iter.org/CODAC/PlantSystemConfig/2014","xsi": "http://www.w3.org/2001/XMLSchema-instance"}
xmlRoot = tree.getroot()
fullVarName="D1-IA-TST2:CMC1CFBS00-WPS00"
perfStartTime = timeit.default_timer() 
r = xmlRoot.find(".//ns0:record[ns0:name='{0}']".format(fullVarName), xmlns)
configurationContainerFullPath = "{{{0}}}configurationContainer".format(xmlns["ns0"])

for a in r.iterancestors():
    n = a.find("./ns0:name", xmlns)
    if (a.tag != configurationContainerFullPath):
        if n is not None:
            fullVarName = n.text + "@" + fullVarName
perfElapsedTime = timeit.default_timer() - perfStartTime

print "{0} {1}".format(fullVarName, perfElapsedTime)

