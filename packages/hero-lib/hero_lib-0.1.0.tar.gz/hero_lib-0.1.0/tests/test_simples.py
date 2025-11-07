import pytest
from hero_lib.models import Hero, Team # Importa os modelos da sua lib

def test_team_creation():
    """
    Testa se uma instância de Team pode ser criada.
    """
    team = Team(name="Avengers")
    assert team.name == "Avengers"

def test_hero_creation():
    """
    Testa se uma instância de Hero pode ser criada.
    """
    hero = Hero(
        name="Spider-Man",
        secret_name="Peter Parker"
    )
    assert hero.name == "Spider-Man"
    assert hero.secret_name == "Peter Parker"