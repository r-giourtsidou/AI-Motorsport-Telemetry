import fastf1
import matplotlib.pyplot as plt



def load_race_session(year: int, event: str):
    """Load a Formula 1 race session using FastF1"""
    print(f"Loading {year} {event} race session...")

    session = fastf1.get_session(year, event, "R")
    session.load()

    print("Session loaded successfully.")
    print(f"Event: {session.event['EventName']}")
    print(f"Date: {session.date}")

    print("\nDrivers in this session:")
    print(session.drivers)

    print("\nDriver information:")
    print(session.results[['Abbreviation', 'FullName', 'TeamName']])



    return session



if __name__ == "__main__":
    race_session = load_race_session(2024, "Monza")
    driver = race_session.laps.pick_driver("HAM")

    print("\nNumber of laps:")
    print(len(driver))

    fastest_lap = driver.pick_fastest()


    print("\nFastest lap:")
    print(fastest_lap)


    telemetry = fastest_lap.get_telemetry()


    print("\nTelemetry preview:")
    print(telemetry.head())




    fig, axes = plt.subplots(3, 1, figsize = (12, 8), sharex = True)

    axes[0].plot(telemetry["Distance"], telemetry["Speed"])

    axes[0].set_title("Hamilton - Fastest Lap Telemetry")
    axes[0].set_ylabel("Speed (km/h)")
    axes[0].grid(True)

    
    axes[1].plot(telemetry["Distance"], telemetry["Throttle"])

    axes[1].set_ylabel("Throttle (%)")
    axes[1].grid(True)


    axes[2].plot(telemetry["Distance"], telemetry["Brake"].astype(int))

    axes[2].set_xlabel("Distance (m)")
    axes[2].set_ylabel("Brake")
    axes[2].grid(True)

    plt.tight_layout()

    plt.savefig("figures/hamilton_telemetry_dashboard.png", dpi=300)

    plt.show()

