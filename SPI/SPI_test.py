import spidev
import time

# SPI GPIO pins for Raspberry Pi 4
# GPIO 10 (MOSI), GPIO 9 (MISO), GPIO 11 (SCLK), GPIO 8 (CS)

# Initialize SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # Open SPI bus 0, device (CS) 0
spi.max_speed_hz = 1000000  # Set SPI speed to 1 MHz
spi.mode = 0b00  # SPI mode 0

# Commands to send to the PSoC
CMD_CLOSE_SERVO_1 = 0x01
CMD_OPEN_SERVO_1 = 0x02
CMD_OPEN_SERVO_2 = 0x03
CMD_CLOSE_SERVO_2 = 0x04

def send_command(command):
    """Send a command to the PSoC via SPI."""
    try:
        response = spi.xfer2([command])  # Send command and get response
        print(f"Sent command: 0x{command:02X}, Received: {response}")
    except Exception as e:
        print(f"Error: {e}")

# Test sequence
try:
    while True:
        print("Sending command to CLOSE Servo 1")
        send_command(CMD_CLOSE_SERVO_1)
        time.sleep(2)  # Wait for 2 seconds

        print("Sending command to OPEN Servo 1")
        send_command(CMD_OPEN_SERVO_1)
        time.sleep(2)  # Wait for 2 seconds

        print("Sending command to OPEN Servo 2")
        send_command(CMD_OPEN_SERVO_2)
        time.sleep(2)  # Wait for 2 seconds

        print("Sending command to CLOSE Servo 2")
        send_command(CMD_CLOSE_SERVO_2)
        time.sleep(2) # Wait for 2 seconds

except KeyboardInterrupt:
    print("\nExiting test program...")
finally:
    spi.close()
