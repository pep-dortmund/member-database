from .models.person import Person, User


def get_user_by_name_or_email(name_or_email):
    return User.query.filter(
        (User.username == name_or_email) | (Person.email == name_or_email)
    ).one_or_none()
