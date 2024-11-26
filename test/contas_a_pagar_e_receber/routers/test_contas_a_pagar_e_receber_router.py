from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from shared.database import Base
from shared.dependencies import get_db

client = TestClient(app)

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


def test_deve_listar_contas_a_pagar_e_receber():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    client.post("/contas-a-pagar-e-receber", json={'descricao': 'Aluguel', 'valor': '1000.50', 'tipo': 'PAGAR'})
    client.post("/contas-a-pagar-e-receber", json={'descricao': 'Salário', 'valor': '5000.00', 'tipo': 'RECEBER'})

    response = client.get('/contas-a-pagar-e-receber')
    assert response.status_code == 200

    assert response.json() == [{'id': 1, 'descricao': 'Aluguel', 'valor': '1000.50', 'tipo': 'PAGAR'},
                               {'id': 2, 'descricao': 'Salário', 'valor': '5000.00', 'tipo': 'RECEBER'}]


def test_deve_criar_conta_a_pagar_e_receber():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    nova_conta = {
        "descricao": "Curso de Python",
        "valor": "333.00",
        "tipo": "PAGAR"
    }
    nova_conta_copy = nova_conta.copy()
    nova_conta_copy["id"] = 1

    response = client.post("/contas-a-pagar-e-receber", json=nova_conta)
    assert response.status_code == 201
    assert response.json() == nova_conta_copy
