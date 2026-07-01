
import pytest
from starlette.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.deps import get_db
from app.db.database import engine



@pytest.fixture()
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture()
def client(db):
    def override_get_db():
        yield db
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear() # Cleanup

# @pytest.fixture()
# def create_user(db):
#     from app.models.users import User
#     from app.core.security import hash_password

#     def _create_user(email="user1@example.com",
#             password=hash_password("password123"),
#             organisation_name="NewCorp"):
#         new_user = User(
#             email=email,
#             password=hash_password(password),
#             organisation_name=organisation_name
#             )
        
#         db.add(new_user)
#         db.commit()
#         db.refresh(new_user)

#         return new_user
    
#     return _create_user
    