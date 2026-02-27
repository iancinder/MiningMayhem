import time
import ntcore
from smbus2 import SMBus

# --- Configuration ---
I2C_ADDRESS = 0x08  # Arduino's address
BUS = SMBus(1)      # Pi 5 uses I2C bus 1
CAMERA_NAME = "YOUR_CAMERA_NAME" # Update this to match your PhotonVision dashboard

# --- NetworkTables Setup ---
nt_inst = ntcore.NetworkTableInstance.getDefault()
nt_inst.startClient4("pi_vision_client")
nt_inst.setServer("127.0.0.1") # Localhost, because script and PV run on the same Pi
vision_table = nt_inst.getTable(f"photonvision/{CAMERA_NAME}")

def send_motor_speeds(left_speed, right_speed):
    """
    Speeds: -100 (reverse) to 100 (forward).
    Mapped to 0-255 (128 = stop) for stable single-byte I2C transmission.
    """
    left_byte = max(0, min(255, int(left_speed + 128)))
    right_byte = max(0, min(255, int(right_speed + 128)))
    
    try:
        BUS.write_i2c_block_data(I2C_ADDRESS, 0, [left_byte, right_byte])
    except OSError as e:
        print(f"I2C Error: Is the Arduino connected and powered? ({e})")

# --- Main Control Loop ---
BASE_SPEED = 40  # Forward speed when rock is detected
KP = 1.5         # Proportional steering gain

print("Mining Mayhem Vision Loop Started...")
while True:
    has_target = vision_table.getBoolean("hasTarget", False)
    
    if has_target:
        target_yaw = vision_table.getNumber("targetYaw", 0.0)
        
        # Calculate differential steering. 
        steering_adjust = target_yaw * KP
        
        left_motor = BASE_SPEED + steering_adjust
        right_motor = BASE_SPEED - steering_adjust
        
        send_motor_speeds(left_motor, right_motor)
        print(f"Tracking | Yaw: {target_yaw:.2f} | L: {left_motor:.0f} R: {right_motor:.0f}")
    else:
        # Halt motors if rock is lost
        send_motor_speeds(0, 0)
        
    time.sleep(0.05) # 20Hz loop