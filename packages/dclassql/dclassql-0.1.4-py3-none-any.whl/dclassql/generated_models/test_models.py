from dataclasses import dataclass
from datetime import datetime

__datasource__ = {
    "provider": "sqlite",
    "url": "sqlite:///test.db",
}

@dataclass
class User:
    id: int
    name: str
    email: str
    last_login: datetime
    birthday: 'BirthDay | None'
    addresses: list['Address']
    books: list['UserBook']

    def index(self):
        yield self.name
        yield self.name, self.email
        yield self.last_login

    def unique_index(self):
        yield self.name, self.email

@dataclass
class Address:
    id: int
    location: str
    user_id: int
    user: 'User'

    def foreign_key(self):
        yield self.user.id == self.user_id, User.addresses


@dataclass
class BirthDay:
    user_id: int
    user: 'User'
    date: datetime

    def primary_key(self):
        return self.user_id

    def foreign_key(self):
        yield self.user.id == self.user_id, User.birthday


@dataclass
class Book:
    id: int
    name: str
    users: list['UserBook']

    def index(self):
        return self.name


@dataclass
class UserBook:
    user_id: int
    book_id: int
    user: User
    book: Book
    created_at: datetime

    def primary_key(self):
        return (self.user_id, self.book_id)

    def index(self):
        yield self.created_at

    def foreign_key(self):
        yield self.user.id == self.user_id, User.books
        yield self.book.id == self.book_id, Book.users

