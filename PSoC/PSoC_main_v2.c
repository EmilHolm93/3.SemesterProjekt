#include "project.h"

// Define pulse width range for the two PWM channels
#define OPEN 750   // OPEN position for servo
#define CLOSED 1700  // CLOSED position for servo

int servo_1_compare = OPEN;
int servo_2_compare = CLOSED;

// ISR for handling SPI receive interrupt
CY_ISR(SPI_Receive_ISR)
{
    
    // Check if SPI data is available in the Rx buffer
    while (SPIS_GetRxBufferSize() > 0)
    {
        // Read the received data
        uint8_t spi_rx_buffer = SPIS_ReadRxData();

        // Interpret SPI commands
        switch (spi_rx_buffer)
        {
            case 0x01: // Command to close Servo 1
                servo_1_compare = CLOSED;
                SPIS_WriteTxData(1);
                break;

            case 0x02: // Command to open Servo 1
                servo_1_compare = OPEN;
                SPIS_WriteTxData(2);
                break;

            case 0x03: // Command to open Servo 2
                servo_2_compare = OPEN;
                SPIS_WriteTxData(3);
                break;

            case 0x04: // Command to close Servo 2
                servo_2_compare = CLOSED;
                SPIS_WriteTxData(4);
                break;
            
            default:
                // Handle invalid or unknown commands if necessary
                SPIS_WriteTxData(9);
                break;
        }
    }

    // Clear the interrupt by reading the Rx status register
    SPIS_ClearRxBuffer();
}

int main(void)
{
    CyGlobalIntEnable; // Enable global interrupts

    // Start PWM and SPI Slave components
    PWM_Start();
    SPIS_Start();

    // Enable Rx Interrupt Mode for "Rx FIFO Not Empty"
    SPIS_SetRxInterruptMode(SPIS_STS_RX_FIFO_NOT_EMPTY);

    // Attach the ISR to the SPI Rx interrupt signal
    isr_1_StartEx(SPI_Receive_ISR);

    for (;;)
    {
        PWM_WriteCompare1(servo_1_compare);
        PWM_WriteCompare2(servo_2_compare);
    }
}