from datetime import date

import bcrypt
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.booking import Booking, BookingStatus, MealSlot
from app.models.chef import Chef
from app.models.dish import Dish
from app.models.user import User

CHEFS = [
    {
        "name": "Chef Ananya Rao",
        "cuisine": "Indian",
        "locality": "Indirapuram",
        "rating": 4.9,
        "price_per_meal": 850,
        "signature_dish": "Butter Chicken",
        "experience_years": 8,
        "bio": "Specializes in North Indian home-style cooking and traditional family recipes.",
        "is_available": True,
        "dishes": [
            {
                "name": "Butter Chicken",
                "description": "Tandoori chicken simmered in a rich tomato and butter gravy.",
                "price": 450,
            },
            {
                "name": "Dal Makhani",
                "description": "Slow-cooked black lentils in a creamy tomato gravy.",
                "price": 280,
            },
            {
                "name": "Garlic Naan",
                "description": "Fluffy tandoor-baked flatbread topped with garlic and butter.",
                "price": 120,
            },
        ],
    },
    {
        "name": "Chef Arjun Malhotra",
        "cuisine": "Punjabi",
        "locality": "Vaishali",
        "rating": 4.7,
        "price_per_meal": 750,
        "signature_dish": "Amritsari Chicken",
        "experience_years": 6,
        "bio": "Known for authentic Punjabi meals, rich curries and traditional tandoor dishes.",
        "is_available": True,
        "dishes": [
            {
                "name": "Amritsari Chicken",
                "description": "Spicy Amritsari-style chicken curry cooked in a rustic blend of spices.",
                "price": 420,
            },
            {
                "name": "Chole Bhature",
                "description": "Chickpea curry served with fluffy fried bhature bread.",
                "price": 250,
            },
            {
                "name": "Paneer Tikka",
                "description": "Char-grilled paneer cubes marinated in spiced yogurt.",
                "price": 320,
            },
        ],
    },
    {
        "name": "Chef Meera Iyer",
        "cuisine": "South Indian",
        "locality": "Noida",
        "rating": 4.8,
        "price_per_meal": 700,
        "signature_dish": "Masala Dosa",
        "experience_years": 7,
        "bio": "Specializes in South Indian vegetarian cuisine and traditional regional recipes.",
        "is_available": True,
        "dishes": [
            {
                "name": "Masala Dosa",
                "description": "Crispy rice and lentil crepe stuffed with spiced potato filling.",
                "price": 220,
            },
            {
                "name": "Idli Sambar",
                "description": "Steamed rice cakes served with lentil sambar and chutney.",
                "price": 180,
            },
            {
                "name": "Vegetable Uttapam",
                "description": "Thick savory pancake topped with mixed vegetables.",
                "price": 200,
            },
        ],
    },
    {
        "name": "Chef Kabir Khan",
        "cuisine": "Continental",
        "locality": "Sector 62",
        "rating": 4.6,
        "price_per_meal": 950,
        "signature_dish": "Creamy Mushroom Pasta",
        "experience_years": 5,
        "bio": "Creates modern continental dishes and restaurant-style meals from home.",
        "is_available": True,
        "dishes": [
            {
                "name": "Creamy Mushroom Pasta",
                "description": "Fettuccine tossed in a creamy garlic mushroom sauce.",
                "price": 420,
            },
            {
                "name": "Grilled Chicken",
                "description": "Herb-marinated chicken breast grilled to perfection.",
                "price": 520,
            },
            {
                "name": "Garlic Bread",
                "description": "Toasted bread brushed with garlic butter and herbs.",
                "price": 180,
            },
        ],
    },
]

USERS = [
    {
        "name": "Aarav Sharma",
        "email": "aarav.sharma@example.com",
        "password": "Chef@1234",
    },
    {
        "name": "Priya Singh",
        "email": "priya.singh@example.com",
        "password": "Chef@1234",
    },
    {
        "name": "Rohan Verma",
        "email": "rohan.verma@example.com",
        "password": "Chef@1234",
    },
]

BOOKINGS = [
    {
        "user_email": "aarav.sharma@example.com",
        "chef_name": "Chef Ananya Rao",
        "booking_date": date(2026, 8, 25),
        "meal_slot": MealSlot.LUNCH,
        "status": BookingStatus.CONFIRMED,
        "special_requests": "Please keep the spice level mild.",
    },
    {
        "user_email": "priya.singh@example.com",
        "chef_name": "Chef Arjun Malhotra",
        "booking_date": date(2026, 8, 26),
        "meal_slot": MealSlot.DINNER,
        "status": BookingStatus.PENDING,
        "special_requests": None,
    },
    {
        "user_email": "rohan.verma@example.com",
        "chef_name": "Chef Meera Iyer",
        "booking_date": date(2026, 8, 27),
        "meal_slot": MealSlot.LUNCH,
        "status": BookingStatus.CHEF_EN_ROUTE,
        "special_requests": "Vegetarian only.",
    },
    {
        "user_email": "aarav.sharma@example.com",
        "chef_name": "Chef Kabir Khan",
        "booking_date": date(2026, 8, 28),
        "meal_slot": MealSlot.DINNER,
        "status": BookingStatus.PENDING,
        "special_requests": None,
    },
]


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def seed_database(session: Session, *, overwrite: bool = False) -> None:
    chef_count = session.scalar(select(func.count()).select_from(Chef))
    if chef_count and not overwrite:
        return

    if overwrite:
        session.query(Booking).delete()
        session.query(Dish).delete()
        session.query(Chef).delete()
        session.query(User).delete()
        session.flush()

    chefs = {}
    for data in CHEFS:
        chef = Chef(
            name=data["name"],
            cuisine=data["cuisine"],
            locality=data["locality"],
            rating=data["rating"],
            price_per_meal=data["price_per_meal"],
            signature_dish=data["signature_dish"],
            experience_years=data["experience_years"],
            bio=data["bio"],
            is_available=data["is_available"],
        )
        session.add(chef)
        session.flush()
        for dish_data in data["dishes"]:
            session.add(
                Dish(
                    chef_id=chef.id,
                    name=dish_data["name"],
                    description=dish_data["description"],
                    price=dish_data["price"],
                )
            )
        chefs[chef.name] = chef

    user_ids = {}
    for user_data in USERS:
        user = User(
            name=user_data["name"],
            email=user_data["email"],
            password_hash=_hash_password(user_data["password"]),
        )
        session.add(user)
        session.flush()
        user_ids[user.email] = user.id

    for booking_data in BOOKINGS:
        session.add(
            Booking(
                user_id=user_ids[booking_data["user_email"]],
                chef_id=chefs[booking_data["chef_name"]].id,
                booking_date=booking_data["booking_date"],
                meal_slot=booking_data["meal_slot"],
                status=booking_data["status"],
                special_requests=booking_data["special_requests"],
            )
        )

    session.commit()