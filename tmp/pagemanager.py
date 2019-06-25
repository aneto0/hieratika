import logging
from xml.etree import cElementTree
from page import Page

log = logging.getLogger("psps-{0}".format(__name__))

class PageManager(object):
    """ Manages all the system Pages.
        Pages are html based user-interfaces that group a collection of variables.
    """

    def __init__(self):
        """Default constructor.
        """
        self.pages = []
        log.debug("Created PageManager")
        self.xmlns = {"ns0": "http://www.iter.org/CODAC/PlantSystemConfig/2014"}

    def load(self, pageXml):
        """Loads a list of pages from an xml file.
           Args:
               pageXml (string): path to the file which contains the page definitions.

           Returns:
               True if the file can be sucessfully loaded.
        """
        ok = True
        log.info("Loading xml: {0}".format(pageXml))
        try:
            root = cElementTree.parse(pageXml)
            #Get all pages
            pagesXml = root.findall(".//ns0:page", self.xmlns)
            for pageXml in pagesXml:
                pageName = pageXml.find("./ns0:name", self.xmlns).text
                pageUrl = pageXml.find("./ns0:url", self.xmlns).text
                pageDescription = pageXml.find("./ns0:description", self.xmlns).text
                page = Page(pageName, pageUrl, pageDescription)
                self.pages.append(page)
                
                log.info("Registered page: {0}".format(page))
        except Exception as e:
            log.critical("Error loading xml file {0} : {1}".format(pageXml, str(e)))
            ok = False

        return ok

    def getPages(self):
        """ Gets all the available pages.

        Returns:
            All the available pages.
        """
        return self.pages


    def getPage(self, name):
        """Gets the page associated to a given name

           Args:
               token (str): the page name to query.

           Returns:
               The Page or None if the name is not found.
        """
        try:
            page = self.pages.index(name)
        except KeyError:
            page = None
        return page

    def __str__(self):
        """Returns a string representation of a list with all the pages that are available.
        """
        return str(map(str, self.pages))
