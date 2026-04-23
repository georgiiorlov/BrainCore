import re


NAME_PATTERN = r"^[A-Za-zA-Яа-яЁё\-]{2,50}$"
PHONE_PATTERN = r"^\+?\d{10,15}$"
EMAIL_PATTERN = r"^[\w\.-]+@[\w\.-]+\.\w+$"
PASSWORD_PATTERN = r"^(?=.*[A-Za-z])(?=.*\d).{8,64}$"

def get_name(name: str) -> str:
    name = name.strip()
    if not re.match(NAME_PATTERN, name):
        raise ValueError("Имя должно содержать только буквы и дефис (2-50 символов)")
    return name


def get_surname(surname: str) -> str:
    surname = surname.strip()
    if not re.match(NAME_PATTERN, surname):
        raise ValueError("Фамилия должна содержать только буквы и дефис (2-50 символов)")
    return surname


def get_phonenumber(phone: str) -> str:
    phone = phone.strip()
    if not re.match(PHONE_PATTERN, phone):
        raise ValueError("Номер должен содержать 10-15 цифр и может начинаться c +'")
    return phone


def get_age(age: str) -> int:
    try:
        age = int(age)
    except ValueError:
        raise ValueError("Возраст должен быть числом")

    if age < 14 or age > 120:
        raise ValueError("Возраст должен быть в диапазоне 141-20")
    return age


def get_password(password: str) -> str:
    password = password.strip()
    
    if not re.fullmatch(PASSWORD_PATTERN, password):
        raise ValueError(
            "Пароль должен быть длиной 8-64 символа и содержать хотя бы одну букву и одну цифру"
        )
    
    return password


def get_email(email: str) -> str:
    email = email.strip().lower()
    if not re.match(EMAIL_PATTERN, email):
        raise ValueError("Некорректный email")
    return email