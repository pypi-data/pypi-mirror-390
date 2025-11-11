#!/usr/bin/env python3

import time
import serial

PORT = "/dev/ttyACM0"  # Change this if your DexArm is on a different port
BAUDRATE = 115200

# Helper to send a command and optionally wait
def send_cmd(ser, cmd, delay=0.5):
    full_cmd = f"{cmd.strip()}\n"
    ser.write(full_cmd.encode("utf-8"))
    time.sleep(delay)

def main():
    try:
        with serial.Serial(PORT, baudrate=BAUDRATE, timeout=1) as ser:
            time.sleep(2)  # wait for device to initialize

            # Enable motor
            send_cmd(ser, "M17", delay=1.0)

            # Move arm in a square or zigzag pattern
            send_cmd(ser, "G0 X200 Y0 Z0 F5000")
            send_cmd(ser, "G0 X200 Y200 Z0 F5000")
            send_cmd(ser, "G0 X0 Y200 Z0 F5000")
            send_cmd(ser, "G0 X0 Y0 Z0 F5000")
            send_cmd(ser, "G0 X100 Y100 Z-50 F3000")  # dip down
            send_cmd(ser, "G0 X100 Y100 Z0 F3000")    # back up

            # Disable motor
            send_cmd(ser, "M18", delay=0.5)

            print("DexArm move sequence complete.")

    except serial.SerialException as e:
        print(f"Failed to communicate with DexArm: {e}")

if __name__ == "__main__":
    main()
