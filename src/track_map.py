import fastf1
import matplotlib.pyplot as plt
import numpy as np

from matplotlib.collections import LineCollection
from matplotlib.colors import Normalize


YEAR = 2024
EVENT = "Monza"
SESSION_TYPE = "R"
DRIVER = "HAM"

# Load session 
session = fastf1.get_session(YEAR, EVENT, SESSION_TYPE)
session.load()
print("Session loaded succesfully.")

# Get telemetry
driver_laps = session.laps.pick_drivers(DRIVER)
fastest_lap = driver_laps.pick_fastest()
telemetry = fastest_lap.get_telemetry()
print(f"\n{DRIVER} fastest lap:")
print(fastest_lap["LapTime"])
print(telemetry[["X", "Y", "Speed"]].head())


# Create arrays
x = telemetry["X"].to_numpy()
y = telemetry["Y"].to_numpy()
speed = telemetry["Speed"].to_numpy()



# Create points and segments
points = np.array([x,y]).T.reshape(-1, 1, 2)
segments = np.concatenate([points[:-1], points[1:]], axis=1)
print(points.shape)
print(segments.shape)


# Create LineCollection
lc = LineCollection(segments, 
                   cmap = "plasma", 
                   norm = plt.Normalize(speed.min(), speed.max()))
lc.set_array(speed[:-1])



# Create Track map figure
plt.figure(figsize=(13,11))
start_point = telemetry.iloc[0]
finish_point = telemetry.iloc[-1]
#plt.plot(telemetry["X"], telemetry["Y"])
plt.scatter(start_point["X"], 
            start_point["Y"], 
            label = "Start / Finish",
            s = 80,
            color = "green")

# Add LineCollection to the figure
plt.gca().add_collection(lc)

# Add colorbar
plt.colorbar(lc, label = "Speed (km/h)")


# Add START annotation and direction
plt.annotate("START / FINISH",
            xy=(start_point["X"], 
            start_point["Y"]),
            xytext= (20, 20),
            textcoords="offset points",
            arrowprops= dict(arrowstyle="->"))

direction_point = telemetry.iloc[60]
plt.arrow(
    start_point["X"],
    start_point["Y"],
    direction_point["X"] - start_point["X"],
    direction_point["Y"] - start_point["Y"],
    head_width = 200, length_includes_head = True
)

# Add title/axis/grid/legend
plt.title("Monza Track Map")
plt.axis("equal")
plt.grid(True) 
plt.legend()
plt.savefig("figures/monza_speed_map.png",
            dpi = 300,
            bbox_inches = "tight")


plt.show()

