import pytest
from pydantic import ValidationError
from ps_hero_fastapi_lib.model.models import Hero, Team, HeroBase, TeamBase

# --- Dados de Teste ---
TEAM_VALID_NAME = "Z-Team"
HERO_VALID_NAME = "Deadpond"
HERO_VALID_SECRET = "Wade Wilson"
HERO_VALID_AGE = 45

# =========================================================
# 🧪 Testes de Modelos Base
# =========================================================

def test_team_base_creation_ok():
    """Deve criar TeamBase com nome válido."""
    team_base = TeamBase(name=TEAM_VALID_NAME)
    assert team_base.name == TEAM_VALID_NAME
# fim_def

def test_team_base_name_too_short():
    """Deve falhar se o nome do Time for muito curto (min_length=2)."""
    with pytest.raises(ValidationError):
        TeamBase(name="a")
    # fim_with
# fim_def

def test_team_base_name_too_long():
    """Deve falhar se o nome do Time for muito longo (max_length=120)."""
    long_name = "a" * 121
    with pytest.raises(ValidationError):
        TeamBase(name=long_name)
    # fim_with
# fim_def

# ---

def test_hero_base_creation_ok():
    """Deve criar HeroBase com dados válidos."""
    hero_base = HeroBase(
        name=HERO_VALID_NAME,
        secret_name=HERO_VALID_SECRET,
        age=HERO_VALID_AGE
    )
    assert hero_base.name == HERO_VALID_NAME
    assert hero_base.age == HERO_VALID_AGE
# fim_def

def test_hero_base_age_too_low():
    """Deve falhar se a idade for negativa (ge=0)."""
    with pytest.raises(ValidationError):
        HeroBase(name=HERO_VALID_NAME, age=-1)

def test_hero_base_age_too_high():
    """Deve falhar se a idade for muito alta (le=200)."""
    with pytest.raises(ValidationError):
        HeroBase(name=HERO_VALID_NAME, age=201)
    # fim_with
# fim_def

def test_hero_base_name_too_short():
    """Deve falhar se o nome do Herói for muito curto (min_length=2)."""
    with pytest.raises(ValidationError):
        HeroBase(name="b")
    # fim_with
# fim_def

# =========================================================
# 🧪 Testes de Modelos SQL (Relacionamentos)
# =========================================================

def test_team_model_initialization():
    """Deve inicializar o modelo Team corretamente."""
    team = Team(name=TEAM_VALID_NAME, id=1)
    assert team.id == 1
    assert team.name == TEAM_VALID_NAME
    # Verifica se a lista de heroes está vazia, mas inicializada
    assert team.heroes == []
# fim_def

def test_hero_model_initialization():
    """Deve inicializar o modelo Hero corretamente."""
    hero = Hero(name=HERO_VALID_NAME, id=1, team_id=5)
    assert hero.id == 1
    assert hero.team_id == 5
    assert hero.name == HERO_VALID_NAME
    # Verifica se o relacionamento 'team' é None por padrão
    assert hero.team is None
# fim_def

def test_hero_model_relationship_to_team():
    """Deve configurar o relacionamento de Hero para Team."""
    team = Team(name=TEAM_VALID_NAME, id=10)
    hero = Hero(
        name=HERO_VALID_NAME,
        id=1,
        team_id=team.id, # Define a FK
        team=team       # Define o Relationship
    )
    assert hero.team is team
    assert hero.team_id == 10
# fim_def

def test_heroes_model_relationship_to_team():
    """Testa a criação completa e a consistência dos relacionamentos bidirecionais."""
    team = Team(name="Justice League", id=1)
    hero = Hero(name="Superman", secret_name="Clark Kent", id=10, team_id=team.id, team=team)
    
    # Assert
    assert len(team.heroes) == 1
    assert hero.team is team
    assert hero.team_id == team.id # Verifique a sincronização da FK
# fim_def
