from google.appengine.ext import db

from ProvidenceClarity.data.core.model import Model
from ProvidenceClarity.data.core.polymodel import PolyPro


class Ticket(PolyPro):
    pass


class SystemTicket(Ticket):
    pass


class JobTicket(SystemTicket):
    pass


class WorkTicket(SystemTicket):
    pass


class MapperTask(WorkTicket):
    pass


class PipelineTask(WorkTicket):
    pass


class WorkerTask(WorkTicket):
    pass