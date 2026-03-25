from app.repositories.base_repository import Repository

from app.database.models import Users, Urls, UsersUrls

class UserRepository(Repository):
    model = Users

class UrlsRepository(Repository):
    model = Urls

class UserUrlRepository(Repository):
    model = UsersUrls