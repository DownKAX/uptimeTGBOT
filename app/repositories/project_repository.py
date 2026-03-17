from app.repositories.base_repository import Repository

from app.database.models import Users, Urls

class UserRepository(Repository):
    model = Users

class UrlsRepository(Repository):
    model = Urls
