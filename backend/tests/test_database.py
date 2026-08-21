from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import app.models  # noqa: F401  (register models on Base.metadata)
from app.db.database import Base
from app.models import Booking, Chef, Dish, User
from app.seed.seed_data import seed_database


def _make_session() -> Session:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(bind=engine)
    return Session(bind=engine)


def test_metadata_contains_all_four_tables():
    tables = set(Base.metadata.tables.keys())
    assert {"users", "chefs", "dishes", "bookings"} <= tables


def test_foreign_keys_reference_expected_tables():
    fk_map = {}
    for table in Base.metadata.tables.values():
        for column in table.columns:
            for fk in column.foreign_keys:
                fk_map[(table.name, column.name)] = fk.column.table.name

    assert fk_map[("dishes", "chef_id")] == "chefs"
    assert fk_map[("bookings", "user_id")] == "users"
    assert fk_map[("bookings", "chef_id")] == "chefs"


def test_relationships_are_configured():
    assert Chef.dishes.property.mapper.class_ is Dish
    assert Dish.chef.property.mapper.class_ is Chef
    assert User.bookings.property.mapper.class_ is Booking
    assert Chef.bookings.property.mapper.class_ is Booking
    assert Booking.user.property.mapper.class_ is User
    assert Booking.chef.property.mapper.class_ is Chef


def test_seed_data_is_consistent():
    session = _make_session()
    seed_database(session)

    assert session.query(Chef).count() == 11
    assert session.query(Dish).count() == 33
    assert session.query(User).count() == 11
    assert session.query(Booking).count() == 11

    chef_ids = {chef.id for chef in session.query(Chef).all()}
    user_ids = {user.id for user in session.query(User).all()}

    for dish in session.query(Dish).all():
        assert dish.chef_id in chef_ids

    for booking in session.query(Booking).all():
        assert booking.user_id in user_ids
        assert booking.chef_id in chef_ids
        assert booking.meal_slot.value in {"BREAKFAST", "LUNCH", "DINNER"}
        assert booking.status.value in {"PENDING", "CONFIRMED", "CHEF_EN_ROUTE"}

    session.close()


def test_seed_does_not_store_plaintext_passwords():
    session = _make_session()
    seed_database(session)

    for user in session.query(User).all():
        assert not user.password_hash.startswith("Chef@")
        assert user.password_hash.startswith("$2")

    session.close()


def test_seed_is_idempotent():
    session = _make_session()
    seed_database(session)
    seed_database(session)

    assert session.query(Chef).count() == 11
    assert session.query(Dish).count() == 33
    assert session.query(User).count() == 11
    assert session.query(Booking).count() == 11

    session.close()