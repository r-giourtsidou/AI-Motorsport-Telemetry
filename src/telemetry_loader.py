import fastf1



def load_race_session(year: int, event: str):
    """Load a Formula 1 race session using FastF1"""
    print(f"Loading {year} {event} race session...")

    session = fastf1.get_session(year, event, "R")
    session.load()

    print("Session loaded successfully.")
    print(f"Event: {session.event['EventName']}")
    print(f"Date: {session.date}")


    return session



if __name__ == "__main__":
    race_session = load_race_session(2024, "Monza")
    