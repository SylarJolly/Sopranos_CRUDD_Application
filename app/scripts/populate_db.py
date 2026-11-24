from sqlalchemy.orm import Session

from app.database import engine
from app.models import Base, Character

# Main characters from The Sopranos. `status` is one of Alive, Dead, Imprisoned or
# Unknown, `first_season` is the season (1-6) of their first appearance.
characters_data = [
    {
        "name": "Tony Soprano",
        "actor": "James Gandolfini",
        "role": "Boss",
        "status": "Unknown",
        "first_season": 1,
        "last_season": 1
    },
    {
        "name": "Carmela Soprano",
        "actor": "Edie Falco",
        "role": "Wife of Tony",
        "status": "Alive",
        "first_season": 1,
        "last_season": 1
    },
    {
        "name": "Christopher Moltisanti",
        "actor": "Michael Imperioli",
        "role": "Capo",
        "status": "Dead",
        "first_season": 1,
        "last_season": 1
    },
    {
        "name": "Paulie Gualtieri",
        "actor": "Tony Sirico",
        "role": "Capo",
        "status": "Alive",
        "first_season": 1,
        "last_season": 1
    },
    {
        "name": "Silvio Dante",
        "actor": "Steven Van Zandt",
        "role": "Consigliere",
        "status": "Alive",
        "first_season": 1,
        "last_season": 1
    },
    {
        "name": "Dr. Jennifer Melfi",
        "actor": "Lorraine Bracco",
        "role": "Psychiatrist",
        "status": "Alive",
        "first_season": 1,
        "last_season": 1
    },
    {
        "name": "Junior Soprano",
        "actor": "Dominic Chianese",
        "role": "Former Boss",
        "status": "Alive",
        "first_season": 1,
        "last_season": 1
    },
    {
        "name": "Livia Soprano",
        "actor": "Nancy Marchand",
        "role": "Matriarch",
        "status": "Dead",
        "first_season": 1,
        "last_season": 1
    },
    {
        "name": "Adriana La Cerva",
        "actor": "Drea de Matteo",
        "role": "Girlfriend of Christopher",
        "status": "Dead",
        "first_season": 1,
        "last_season": 1
    },
    {
        "name": "Big Pussy Bonpensiero",
        "actor": "Vincent Pastore",
        "role": "Soldier",
        "status": "Dead",
        "first_season": 1,
        "last_season": 1
    },
    {
        "name": "Meadow Soprano",
        "actor": "Jamie-Lynn Sigler",
        "role": "Daughter of Tony",
        "status": "Alive",
        "first_season": 1,
        "last_season": 1
    },
    {
        "name": "A.J. Soprano",
        "actor": "Robert Iler",
        "role": "Son of Tony",
        "status": "Alive",
        "first_season": 1,
        "last_season": 1
    },
]


def populate():
    """Create the table and seed it, but only if it's empty (so your changes survive a restart)."""
    Base.metadata.create_all(bind=engine)
    with Session(bind=engine) as session:
        if session.query(Character).count() > 0:
            return
        for character in characters_data:
            session.add(Character(**character))
        session.commit()


def reset():
    """Wipe the table and re-seed it. Run with `python -m app.scripts.populate_db`"""
    Base.metadata.create_all(bind=engine)
    with Session(bind=engine) as session:
        session.query(Character).delete()
        session.commit()
    populate()


if __name__ == "__main__":
    reset()