from sqlalchemy.orm import Session

from app.database import engine
from app.models import Base, Character

# Main characters from The Sopranos. `status` is one of Alive, Dead, Imprisoned or
# Unknown, `first_season` is the season (1-6) of their first appearance.
characters_data = [
    {
        "name": "Tony Soprano",
        "actor": "James Gandolfini",
        "role": "Boss of the DiMeo Crime Family",
        "status": "Unknown",
        "first_season": 1,
        "last_season": 6
    },
    {
        "name": "Carmela Soprano",
        "actor": "Edie Falco",
        "role": "Tony's Wife",
        "status": "Alive",
        "first_season": 1,
        "last_season": 6
    },
    {
        "name": "Christopher Moltisanti",
        "actor": "Michael Imperioli",
        "role": "Capo in the Soprano Crime Family",
        "status": "Dead",
        "first_season": 1,
        "last_season": 6
    },
    {
        "name": "Paulie Gualtieri",
        "actor": "Tony Sirico",
        "role": "Capo in the Soprano Crime Family",
        "status": "Alive",
        "first_season": 1,
        "last_season": 6
    },
    {
        "name": "Silvio Dante",
        "actor": "Steven Van Zandt",
        "role": "Consigliere to Tony Soprano",
        "status": "Comatose",
        "first_season": 1,
        "last_season": 6
    },
    {
        "name": "Dr. Jennifer Melfi",
        "actor": "Lorraine Bracco",
        "role": "Tony's Psychiatrist",
        "status": "Alive",
        "first_season": 1,
        "last_season": 6
    },
    {
        "name": "Junior Soprano",
        "actor": "Dominic Chianese",
        "role": "Tony's Uncle and Former Boss",
        "status": "Alive",
        "first_season": 1,
        "last_season": 6
    },
    {
        "name": "Livia Soprano",
        "actor": "Nancy Marchand",
        "role": "Tony's Mother",
        "status": "Dead",
        "first_season": 1,
        "last_season": 3
    },
    {
        "name": "Adriana La Cerva",
        "actor": "Drea de Matteo",
        "role": "Christopher's Fiancée",
        "status": "Dead",
        "first_season": 1,
        "last_season": 5
    },
    {
        "name": "Salvatore Bonpensiero",
        "actor": "Vincent Pastore",
        "role": "Soprano Family Soldier and FBI Informant",
        "status": "Dead",
        "first_season": 1,
        "last_season": 2
    },
    {
        "name": "Meadow Soprano",
        "actor": "Jamie-Lynn Sigler",
        "role": "Tony's Daughter",
        "status": "Alive",
        "first_season": 1,
        "last_season": 6
    },
    {
        "name": "A.J. Soprano",
        "actor": "Robert Iler",
        "role": "Tony's Son",
        "status": "Alive",
        "first_season": 1,
        "last_season": 6
    }
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