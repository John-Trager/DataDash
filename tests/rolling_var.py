import csv
import matplotlib.pyplot as plt
import numpy as np


# Function to calculate the rolling variance
def rolling_variance(data, window_size):
    variance = []
    for i in range(len(data) - window_size + 1):
        window = data[i : i + window_size]
        variance.append(np.var(window))
    return variance


accel_x_values = []

with open("/Users/jt-lab/Projects/DashData/roadtest_imu2.csv", "r") as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        accel_x_values.append(float(row["accel x"]))

window_size = 100  # You can adjust this to the desired window size
rolling_variances = rolling_variance(accel_x_values, window_size)

### processing when the car is stopped

in_motion = True
length_not_in_motion = -1
thresh_hold = 0.1  # this is handpicked... (it is important that )
for var_val in rolling_variances:
    if in_motion:
        if abs(var_val) < thresh_hold:
            in_motion = False
            print("Detected Car Stopped")
            length_not_in_motion = 1
    elif not in_motion:
        if abs(var_val) < thresh_hold:
            length_not_in_motion += 1
        else:
            in_motion = True
            print(
                f"Detected Car moving! Lasted {length_not_in_motion} frames not in motion..."
            )
            length_not_in_motion = 0

if length_not_in_motion > 0:
    print(f"Detected Car moving! Lasted {length_not_in_motion} frames not in motion...")
###

plt.plot(accel_x_values, label="Original")
plt.plot(
    range(window_size - 1, len(accel_x_values)),
    rolling_variances,
    label=f"Rolling Variance (Window Size: {window_size})",
)


plt.xlabel("Time")
plt.ylabel("Acceleration (X)")
plt.title("Acceleration X Values with Rolling Variance")
plt.legend()
plt.show()
