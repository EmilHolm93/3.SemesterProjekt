import spidev
import time

# Initialize SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # Open SPI bus 0, device (CS) 0
spi.max_speed_hz = 1000000  # Set SPI speed to 1 MHz
spi.mode = 0b00  # SPI mode 0 (CPOL=0, CPHA=0)

def test_spi():
    """Send a test byte over SPI and print the response."""
    try:
        print("Starting SPI test...")
        while True:
            test_byte = 0xAA  # Test byte to send (0xAA)
            response = spi.xfer2([test_byte])  # Send byte and receive response
            print(f"Sent: 0x{test_byte:02X}, Received: {response[0]}")
            time.sleep(1)  # Wait for 1 second
    except KeyboardInterrupt:
        print("\nExiting SPI test.")
    finally:
        spi.close()

# Run the SPI test
test_spi()
