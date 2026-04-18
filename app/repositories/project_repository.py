from app.repositories.base_repository import Repository

from app.database.models import Users, Urls, UsersUrls, Incidents


class UserRepository(Repository):
    model = Users

class UrlsRepository(Repository):
    model = Urls

class UserUrlRepository(Repository):
    model = UsersUrls

class IncidentRepository(Repository):
    model = Incidents

