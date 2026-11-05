import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data.csv")

time_s = (df["time_ms"] - df["time_ms"].iloc[0]) / 1000.0

fs = 1000.0 / df["time_ms"].diff().mean()
print(f"Sampling rate: {fs:.1f} Hz | Total samples: {len(df)}")

ax_g = df["ax"] / 16384.0
ay_g = df["ay"] / 16384.0
az_g = df["az"] / 16384.0

gx_raw = df["gx"] / 131.072
gy_raw = df["gy"] / 131.072
gz_raw = df["gz"] / 131.072

gx_gps = gx_raw - gx_raw.iloc[-200:].mean()
gy_gps = gy_raw - gy_raw.iloc[-200:].mean()
gz_gps = gz_raw - gz_raw.iloc[-200:].mean()

pan_deg = df["pan_deg"]
tilt_deg = df["tilt_deg"]

err_x = df["err_x"]
err_y = df["err_y"]

plt.figure(figsize=(10, 8))

plt.subplot(4, 1, 1)
plt.plot(time_s, ax_g, label="Ax")
plt.plot(time_s, ay_g, label="Ay")
plt.plot(time_s, az_g, label="Az")
plt.ylabel("Acceleration [g]")
plt.legend()
plt.grid(True)

plt.subplot(4, 1, 2)
plt.plot(time_s, gx_gps, label="Gx")
plt.plot(time_s, gy_gps, label="Gy")
plt.plot(time_s, gz_gps, label="Gz")
plt.ylabel("Gyroscope [deg/s]")
plt.legend()
plt.grid(True)

plt.subplot(4, 1, 3)
plt.step(time_s, pan_deg, where="post", label="Pan angle")
plt.step(time_s, tilt_deg, where="post", label="Tilt angle")
plt.ylabel("Servo [deg]")
plt.legend()
plt.grid(True)

plt.subplot(4, 1, 4)
plt.plot(time_s, err_x, label="Error X")
plt.plot(time_s, err_y, label="Error Y")
plt.axhline(8, color="gray", linestyle="--", linewidth=0.8)
plt.axhline(-8, color="gray", linestyle="--", linewidth=0.8)
plt.ylabel("Error [px]")
plt.xlabel("Time [s]")
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig("docs/imu_100hz_validation.png", dpi=150)
plt.show()