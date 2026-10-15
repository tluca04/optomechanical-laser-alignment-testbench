import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data.csv")

time_s = (df["time_ms"]-df["time_ms"].iloc[0])/1000

fs = 1000.0 / df["time_ms"].diff().mean()
print(f"Sampling rate: {fs:.1f} Hz | Total samples: {len(df)}")

ax_g = df["ax"]/16384
ay_g = df["ay"]/16384
az_g = df["az"]/16384

gx_gps = df["gx"]/131.072
gy_gps = df["gy"]/131.072
gz_gps = df["gz"]/131.072

plt.subplot(2, 1, 1)
plt.plot(time_s, ax_g, label="Ax")
plt.plot(time_s, ay_g, label="Ay")
plt.plot(time_s, az_g, label="Az")
plt.ylabel("Acceleration [g]")
plt.xlabel("Time [s]")
plt.legend()
plt.grid(True)

plt.subplot(2, 1, 2)
plt.plot(time_s, gx_gps, label="Gx")
plt.plot(time_s, gy_gps, label="Gy")
plt.plot(time_s, gz_gps, label="Gz")
plt.ylabel("Gyroscope [deg/s]")
plt.xlabel("Time [s]")
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig("docs/imu_100hz_validation.png", dpi=150)
plt.show()