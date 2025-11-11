from timeback.http import HttpClient
from timeback.services.oneroster.rostering import RosteringService


class OneRosterService:
    """Container for OneRoster services."""

    def __init__(self, http: HttpClient):
        self.rostering = RosteringService(http)
