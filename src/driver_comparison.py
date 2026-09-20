import fastf1
import matplotlib.pyplot as plt

YEAR = 2024 
EVENT = "Monza"
SESSION_TYPE = "R"

DRIVER_1 = "HAM"
DRIVER_2 = "RUS"



print(f"Loading {YEAR} {EVENT} session...")

session = fastf1.get_session(YEAR, EVENT, SESSION_TYPE)

session.load()

print("Session loaded successfully.")

driver_1_laps = session.laps.pick_drivers(DRIVER_1)
driver_2_laps = session.laps.pick_drivers(DRIVER_2)

driver_1_fastest_lap = driver_1_laps.pick_fastest()
driver_2_fastest_lap = driver_2_laps.pick_fastest()



print(f"\n{DRIVER_1} fastest lap:")
print(driver_1_fastest_lap["LapTime"])

print(f"\n{DRIVER_2} fastest lap:")
print(driver_2_fastest_lap["LapTime"])



driver_1_telemetry = driver_1_fastest_lap.get_telemetry()
driver_2_telemetry = driver_2_fastest_lap.get_telemetry()



plt.figure(figsize=(13,11))

plt.subplot(3,1,1)
plt.plot(driver_1_telemetry["Distance"], driver_1_telemetry["Speed"], label = DRIVER_1)
plt.plot(driver_2_telemetry["Distance"], driver_2_telemetry["Speed"], label = DRIVER_2)

plt.title("Hamilton vs Russell - Monza 2024")
plt.ylabel("Speed (km/h)")
plt.grid(True)
plt.legend()


plt.subplot(3,1,2)
plt.plot(driver_1_telemetry["Distance"], driver_1_telemetry["Throttle"])
plt.plot(driver_2_telemetry["Distance"], driver_2_telemetry["Throttle"])
plt.ylabel("Throttle (%)")
plt.grid(True)
plt.legend()


plt.subplot(3,1,3)
plt.plot(driver_1_telemetry["Distance"], driver_1_telemetry["Brake"].astype(int))
plt.plot(driver_2_telemetry["Distance"], driver_2_telemetry["Brake"].astype(int))
plt.xlabel("Distance (m)")
plt.ylabel("Brake")
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.savefig("figures/hamilton_russell_comparison_Monza_2024.png", dpi=300)
plt.show()
