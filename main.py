from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from valid import get_name, get_surname, get_email, get_age, get_phonenumber, get_password
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware


from database import SessionLocal, engine
from models import User
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from models import User, Course
from models import Enrollment


app = FastAPI()
from database import Base
Base.metadata.create_all(bind=engine)

app.add_middleware(SessionMiddleware, secret_key="super-secret-key")
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/",response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("main.html", {"request":request, "message": "Добро пожаловать в BrainCore!"})

@app.get("/success", response_class=HTMLResponse)
async def success(request: Request):
    return templates.TemplateResponse("success.html", {
        "request": request,
        "message": "Регистрация прошла успешно!"
    })
@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    user = request.session.get("user")

    if not user:
        return RedirectResponse(url="/")

    db = SessionLocal()
    courses = db.query(Course).all()
    enrolled_courses = []
    if user["role"] == "student":
        enrollments = db.query(Enrollment).filter(Enrollment.user_email == user["email"]).all()
        enrolled_ids = [e.course_id for e in enrollments]
        enrolled_courses = db.query(Course).filter(Course.id.in_(enrolled_ids)).all()
    db.close()

    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user,
        "courses": courses,
        "enrolled_courses": enrolled_courses
    })
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)

@app.get("/course/{course_id}/students", response_class=HTMLResponse)
async def course_students(request: Request, course_id: int):
    user = request.session.get("user")

    # Только преподаватель имеет доступ
    if not user or user["role"] != "teacher":
        return RedirectResponse(url="/")

    db = SessionLocal()

    # Получаем курс
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        db.close()
        return RedirectResponse(url="/profile")

    # Получаем всех студентов записанных на этот курс
    enrollments = db.query(Enrollment).filter(Enrollment.course_id == course_id).all()
    
    students = []
    for enrollment in enrollments:
        student = db.query(User).filter(User.email == enrollment.user_email).first()
        if student:
            students.append({
                "name": student.name,
                "surname": student.surname,
                "email": student.email,
                "phone": student.phone
            })

    db.close()

    return templates.TemplateResponse("course_students.html", {
        "request": request,
        "course": course,
        "students": students,
        "user": user
    })

@app.post("/", response_class=HTMLResponse)
async def submit(
    request: Request,
    name: str = Form(...),
    surname: str = Form(...),
    phone: str = Form(...),
    age: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(...)
    ):
    db = SessionLocal()
    try:
        name2 = get_name(name)
        surname2 = get_surname(surname)
        phone2 = get_phonenumber(phone)
        age2 = get_age(age)
        email2 = get_email(email)
        password2 = get_password(password)

        existing_user = db.query(User).filter(User.email == email2).first()
        if existing_user:
            raise ValueError("Пользователь c таким email уже существует")
        hashed_password = bcrypt.hash(password2)
        user = User(
            name=name2,
            surname=surname2,
            email=email2,
            password=hashed_password,
            phone=phone2,
            age=age2,
            role=role)
        db.add(user)
        db.commit()
        db.close()
        request.session["user"] = {
            "name": name2,
            "surname": surname2,
            "email": email2,
            "age": age2,
            "phone": phone2,
            "role": role}
        return RedirectResponse(url="/success", status_code=303)
    except Exception as e:
        return templates.TemplateResponse("main.html", {"request": request,"error": str(e)})
    
@app.post("/login")
async def login(request: Request,
                email: str = Form(...),
                password: str = Form(...)):

    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    db.close()

    if not user or not bcrypt.verify(password, user.password):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Неверный логин или пароль"
        })

    request.session["user"] = {
    "name": user.name,
    "surname": user.surname,
    "email": user.email,
    "age": user.age,
    "phone": user.phone,
    "role": user.role}

    return RedirectResponse(url="/profile", status_code=303)

@app.post("/create-course")
async def create_course(
    request: Request,
    title: str = Form(...),
    description: str = Form(...)
):
    user = request.session.get("user")

    if not user or user["role"] != "teacher":
        return RedirectResponse(url="/")

    db = SessionLocal()

    course = Course(title=title, description=description)

    db.add(course)
    db.commit()
    db.close()

    return RedirectResponse(url="/profile", status_code=303)

@app.post("/enroll")
async def enroll(request: Request, course_id: int = Form(...)):
    user = request.session.get("user")

    if not user:
        return RedirectResponse(url="/")

    db = SessionLocal()

    existing = db.query(Enrollment).filter(
        Enrollment.user_email == user["email"],
        Enrollment.course_id == course_id
    ).first()

    if existing:
        db.close()
        return RedirectResponse(url="/profile", status_code=303)

    enrollment = Enrollment(
        user_email=user["email"],
        course_id=course_id
    )

    db.add(enrollment)
    db.commit()
    db.close()

    return RedirectResponse(url="/profile", status_code=303)