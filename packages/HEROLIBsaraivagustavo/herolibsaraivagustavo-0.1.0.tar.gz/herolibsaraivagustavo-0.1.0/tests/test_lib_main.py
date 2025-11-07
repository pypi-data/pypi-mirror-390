from HeroLib.models.models import *
from HeroLib.models.dto import *

import pytest


def createHero():
    hero = HeroCreate(
        name = "Saraiva",
        secret_name = "gussmm",
        age = 20
    )

    assert hero.name == "Saraiva"
    assert hero.secret_name == "gussmm"
    assert hero.age == 20

def createTeam():
    team = TeamCreate(
        name = "Os Calabresos"
    )

    assert team.name == "Os Calabresos"

def test_hero_with_team():
    team = TeamPublic(
        id = 1,
        name = "Os Calabresos"
    )

    hero = HeroPublic(
        id = 1,
        name = "Saraiva",
        secret_name = "gussmm",
        age = 20,
    )

    assert team.id == 1
    assert team.name == "Os Calabresos"

    assert hero.id == 1
    assert hero.name == "Saraiva"


def test_team_with_heroes():
    team = TeamWithHeroes(
        id = 1,
        name = "Os Calabresos",
        heroes = [
            HeroPublic(
                id = 1,
                name = "Saraiva",
                secret_name = "gussmm",
                age = 20,
            )
        ]
    )