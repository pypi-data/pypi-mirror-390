import sys
import json
from typing import Any, Dict, Optional
from lager.pcb.net import Net, NetType

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

def _as_float(v: Optional[Any]) -> Optional[float]:
    if v is None or v == "None":
        return None
    return float(v)

def main() -> int:
    try:
        # Expect a single JSON payload in argv[1], same as thermocouple
        data: Dict[str, Any] = json.loads(sys.argv[1])

        netname: str = data["netname"]
        command: str = data["command"]

        # Optional args
        x   = _as_float(data.get("x"))
        y   = _as_float(data.get("y"))
        z   = _as_float(data.get("z"))
        dx  = _as_float(data.get("dx"))
        dy  = _as_float(data.get("dy"))
        dz  = _as_float(data.get("dz"))
        timeout = _as_float(data.get("timeout")) or 5.0

        # Resolve the Arm net via your Net registry
        arm = Net.get(netname, type=NetType.Arm)

        if command == "position":
            px, py, pz = arm.position()
            sys.stdout.write(f"{GREEN}X: {px} Y: {py} Z: {pz}{RESET}\n")
            sys.stdout.flush()
            return 0

        elif command == "move":
            if x is None or y is None or z is None:
                raise ValueError("move requires x, y, z")
            arm.move_to(x, y, z, timeout=timeout)
            px, py, pz = arm.position()
            sys.stdout.write(f"{GREEN}X: {px} Y: {py} Z: {pz}{RESET}\n")
            sys.stdout.flush()
            return 0

        elif command == "move_by":
            ddx = dx or 0.0
            ddy = dy or 0.0
            ddz = dz or 0.0
            px, py, pz = arm.delta(ddx, ddy, ddz, timeout=timeout)
            sys.stdout.write(f"{GREEN}X: {px} Y: {py} Z: {pz}{RESET}\n")
            sys.stdout.flush()
            return 0

        elif command == "go_home":
            arm.go_home()
            return 0

        elif command == "enable_motor":
            arm.enable_motor()
            return 0

        elif command == "disable_motor":
            arm.disable_motor()
            return 0

        elif command == "read_and_save_position":
            arm.read_and_save_position()
            return 0
        
        elif command == "set_acceleration":
            # required: acceleration, travel_acceleration; optional: retract_acceleration (default=60)
            acceleration = int(data["acceleration"])
            travel_acceleration = int(data["travel_acceleration"])
            retract_acceleration = int(data.get("retract_acceleration", 60))
            arm.set_acceleration(acceleration, travel_acceleration, retract_acceleration=retract_acceleration)
            sys.stdout.write(
                f"{GREEN}Acceleration set (M204): print={acceleration} travel={travel_acceleration} retract={retract_acceleration}{RESET}\n"
            )
            sys.stdout.flush()
            return 0


        else:
            raise ValueError(f"unknown command: {command}")

    except Exception as e:
        sys.stderr.write(f"{RED}{e}{RESET}\n")
        sys.stderr.flush()
        return 1

if __name__ == "__main__":
    sys.exit(main())



# import sys
# import time
# from lager.pydexarm import Dexarm, get_arm_device

# def parse_float(val):
#     if val == 'None':
#         return None
#     return float(val)

# def print_position(position):
#     (x, y, z, extrusion, theta_a, theta_b, theta_c) = position
#     print(f'X: {x} Y: {y} Z: {z}')

# def get_position(device):
#     with Dexarm(port=device) as arm:
#         position = arm.get_current_position()
#         print_position(position)

# def disable_motor(device):
#     with Dexarm(port=device) as arm:
#         arm.disable_motor()

# def enable_motor(device):
#     with Dexarm(port=device) as arm:
#         arm.enable_motor()

# def read_and_save_position(device):
#     with Dexarm(port=device) as arm:
#         arm.read_and_save_position()

# def delta(device):
#     with Dexarm(port=device) as arm:
#         (x, y, z, extrusion, theta_a, theta_b, theta_c) = arm.get_current_position()

#         delta_x = parse_float(sys.argv[2]) or 0.0
#         delta_y = parse_float(sys.argv[3]) or 0.0
#         delta_z = parse_float(sys.argv[4]) or 0.0

#         new_x = delta_x + x
#         new_y = delta_y + y
#         new_z = delta_z + z

#         arm.move_to_blocking(new_x, new_y, new_z, timeout=5.0)
#         time.sleep(0.1)
#         position = arm.get_current_position()
#         print_position(position)


# def move(device):
#     with Dexarm(port=device) as arm:
#         (x, y, z, extrusion, theta_a, theta_b, theta_c) = arm.get_current_position()

#         x = parse_float(sys.argv[2]) or x
#         y = parse_float(sys.argv[3]) or y
#         z = parse_float(sys.argv[4]) or z
#         arm.move_to_blocking(x, y, z, timeout=5.0)

#         time.sleep(0.1)
#         position = arm.get_current_position()
#         print_position(position)

# def go_home(device):
#     with Dexarm(port=device) as arm:
#         arm.go_home()    

# def main():

#     command = sys.argv[1]
#     serial = sys.argv[-1]
#     if serial == 'None':
#         serial = None
#     device = get_arm_device(serial)

#     if command == 'position':
#         get_position(device)
#     elif command == 'disable_motor':
#         disable_motor(device)
#     elif command == 'enable_motor':
#         enable_motor(device)
#     elif command == 'read_and_save_position':
#         read_and_save_position(device)
#     elif command == 'delta':
#         delta(device)
#     elif command == 'move':
#         move(device)
#     elif command == 'go_home':
#         go_home(device)


# if __name__ == '__main__':
#     main()
