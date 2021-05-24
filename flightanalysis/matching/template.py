

from flightanalysis.schedule import Schedule, Manoeuvre, Element, ElClass, Categories
from flightanalysis.section import Section




class MatchedElement(object):
    def __init__(self, element: Element, template: Section, flown: Section):
        self.element = element
        self.template = template
        self.flown = flown
    
    