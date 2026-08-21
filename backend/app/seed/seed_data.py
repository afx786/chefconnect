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
    {
        "name": "Chef Kavita Menon",
        "cuisine": "Kerala",
        "locality": "Greater Noida",
        "rating": 4.5,
        "price_per_meal": 800,
        "signature_dish": "Kerala Fish Curry",
        "experience_years": 9,
        "bio": "Specializes in coastal Kerala cuisine with coconut-based curries and fresh seafood.",
        "is_available": True,
        "dishes": [
            {
                "name": "Kerala Fish Curry",
                "description": "Meen curry cooked in tangy coconut and kokum gravy.",
                "price": 380,
            },
            {
                "name": "Appam",
                "description": "Soft, lacy fermented rice pancakes from the Malabar coast.",
                "price": 150,
            },
            {
                "name": "Avial",
                "description": "Mixed vegetables simmered in a creamy coconut and yogurt sauce.",
                "price": 220,
            },
        ],
    },
    {
        "name": "Chef Lakshmi Narayan",
        "cuisine": "Bengali",
        "locality": "Crossings Republik",
        "rating": 4.4,
        "price_per_meal": 720,
        "signature_dish": "Kosha Mangsho",
        "experience_years": 10,
        "bio": "Authentic Bengali home cooking with rich curries and traditional sweets.",
        "is_available": True,
        "dishes": [
            {
                "name": "Kosha Mangsho",
                "description": "Slow-cooked spicy mutton curry in the Bengali style.",
                "price": 450,
            },
            {
                "name": "Bhapa Ilish",
                "description": "Hilsa fish steamed in mustard and green chili paste.",
                "price": 420,
            },
            {
                "name": "Mishti Doi",
                "description": "Caramelized sweet yogurt set in clay pots.",
                "price": 150,
            },
        ],
    },
    {
        "name": "Chef Farhan Qureshi",
        "cuisine": "Mughlai",
        "locality": "Sector 18",
        "rating": 4.8,
        "price_per_meal": 980,
        "signature_dish": "Chicken Biryani",
        "experience_years": 12,
        "bio": "Mughlai delicacies, aromatic biryanis and slow-cooked kebab specialties.",
        "is_available": True,
        "dishes": [
            {
                "name": "Chicken Biryani",
                "description": "Fragrant basmati rice layered with spiced chicken and saffron.",
                "price": 380,
            },
            {
                "name": "Galouti Kebab",
                "description": "Melt-in-the-mouth minced meat kebabs with aromatic spices.",
                "price": 350,
            },
            {
                "name": "Sheermal",
                "description": "Saffron-sweetened leavened flatbread from royal kitchens.",
                "price": 120,
            },
        ],
    },
    {
        "name": "Chef Anjali Deshpande",
        "cuisine": "Maharashtrian",
        "locality": "Indirapuram",
        "rating": 4.6,
        "price_per_meal": 680,
        "signature_dish": "Puran Poli",
        "experience_years": 7,
        "bio": "Home-style Maharashtrian vegetarian cooking and festive traditional dishes.",
        "is_available": True,
        "dishes": [
            {
                "name": "Puran Poli",
                "description": "Sweet stuffed flatbread with chana dal and jaggery.",
                "price": 180,
            },
            {
                "name": "Misal Pav",
                "description": "Spicy sprouted bean curry served with soft pav.",
                "price": 150,
            },
            {
                "name": "Kolhapuri Mutton",
                "description": "Fiery mutton curry with the signature Kolhapuri masala.",
                "price": 420,
            },
        ],
    },
    {
        "name": "Chef Vikramaditya Singh",
        "cuisine": "Awadhi",
        "locality": "Raj Nagar",
        "rating": 4.7,
        "price_per_meal": 890,
        "signature_dish": "Lucknowi Biryani",
        "experience_years": 11,
        "bio": "Regal Awadhi cuisine with dum-cooked biryanis and delicate kebabs.",
        "is_available": True,
        "dishes": [
            {
                "name": "Lucknowi Biryani",
                "description": "Dum-cooked basmati rice with tender meat and saffron.",
                "price": 400,
            },
            {
                "name": "Kakori Kebab",
                "description": "Soft, spiced minced meat kebabs from the royal Awadhi kitchen.",
                "price": 380,
            },
            {
                "name": "Roomali Roti",
                "description": "Paper-thin hand-stretched flatbread.",
                "price": 80,
            },
        ],
    },
    {
        "name": "Chef Sneha Kapoor",
        "cuisine": "Asian Fusion",
        "locality": "Sector 50",
        "rating": 4.5,
        "price_per_meal": 850,
        "signature_dish": "Thai Basil Chicken",
        "experience_years": 6,
        "bio": "Modern Asian fusion bowls, stir-fries and restaurant-style presentations.",
        "is_available": True,
        "dishes": [
            {
                "name": "Thai Basil Chicken",
                "description": "Stir-fried chicken with Thai basil, chili and soy glaze.",
                "price": 420,
            },
            {
                "name": "Sticky Rice",
                "description": "Sweet steamed glutinous rice.",
                "price": 150,
            },
            {
                "name": "Veg Spring Rolls",
                "description": "Crispy rolls filled with seasoned vegetables.",
                "price": 200,
            },
        ],
    },
    {
        "name": "Chef Imran Ali",
        "cuisine": "Hyderabadi",
        "locality": "Vasundhara",
        "rating": 4.6,
        "price_per_meal": 820,
        "signature_dish": "Hyderabadi Biryani",
        "experience_years": 8,
        "bio": "Nizami Hyderabadi cuisine with fragrant dum biryanis and rich curries.",
        "is_available": True,
        "dishes": [
            {
                "name": "Hyderabadi Biryani",
                "description": "Dum-cooked biryani with saffron, mint and caramelized onions.",
                "price": 420,
            },
            {
                "name": "Haleem",
                "description": "Slow-cooked wheat, lentil and meat porridge with spices.",
                "price": 350,
            },
            {
                "name": "Mirchi Ka Salan",
                "description": "Tangy peanut and sesame gravy with green chilies.",
                "price": 150,
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
    {
        "name": "Ishaan Gupta",
        "email": "ishaan.gupta@example.com",
        "password": "Chef@1234",
    },
    {
        "name": "Neha Kapoor",
        "email": "neha.kapoor@example.com",
        "password": "Chef@1234",
    },
    {
        "name": "Aditya Nair",
        "email": "aditya.nair@example.com",
        "password": "Chef@1234",
    },
    {
        "name": "Sana Sheikh",
        "email": "sana.sheikh@example.com",
        "password": "Chef@1234",
    },
    {
        "name": "Karan Malhotra",
        "email": "karan.malhotra@example.com",
        "password": "Chef@1234",
    },
    {
        "name": "Divya Pillai",
        "email": "divya.pillai@example.com",
        "password": "Chef@1234",
    },
    {
        "name": "Arjun Reddy",
        "email": "arjun.reddy@example.com",
        "password": "Chef@1234",
    },
    {
        "name": "Tanvi Kulkarni",
        "email": "tanvi.kulkarni@example.com",
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
    {
        "user_email": "ishaan.gupta@example.com",
        "chef_name": "Chef Kavita Menon",
        "booking_date": date(2026, 8, 29),
        "meal_slot": MealSlot.DINNER,
        "status": BookingStatus.PENDING,
        "special_requests": None,
    },
    {
        "user_email": "neha.kapoor@example.com",
        "chef_name": "Chef Farhan Qureshi",
        "booking_date": date(2026, 8, 30),
        "meal_slot": MealSlot.LUNCH,
        "status": BookingStatus.CONFIRMED,
        "special_requests": "Extra spicy please.",
    },
    {
        "user_email": "aditya.nair@example.com",
        "chef_name": "Chef Lakshmi Narayan",
        "booking_date": date(2026, 8, 31),
        "meal_slot": MealSlot.DINNER,
        "status": BookingStatus.CONFIRMED,
        "special_requests": None,
    },
    {
        "user_email": "sana.sheikh@example.com",
        "chef_name": "Chef Anjali Deshpande",
        "booking_date": date(2026, 9, 1),
        "meal_slot": MealSlot.LUNCH,
        "status": BookingStatus.PENDING,
        "special_requests": "Vegetarian Jain meal.",
    },
    {
        "user_email": "karan.malhotra@example.com",
        "chef_name": "Chef Vikramaditya Singh",
        "booking_date": date(2026, 9, 2),
        "meal_slot": MealSlot.DINNER,
        "status": BookingStatus.CHEF_EN_ROUTE,
        "special_requests": "Celebration dinner.",
    },
    {
        "user_email": "divya.pillai@example.com",
        "chef_name": "Chef Sneha Kapoor",
        "booking_date": date(2026, 9, 3),
        "meal_slot": MealSlot.LUNCH,
        "status": BookingStatus.PENDING,
        "special_requests": None,
    },
    {
        "user_email": "tanvi.kulkarni@example.com",
        "chef_name": "Chef Imran Ali",
        "booking_date": date(2026, 9, 4),
        "meal_slot": MealSlot.DINNER,
        "status": BookingStatus.CONFIRMED,
        "special_requests": "Mild spice level.",
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