#include "project.h"
#include "UART.h"

CY_ISR_PROTO(ISR_UART_rx_handler);

void handleByteReceived(uint8_t byteReceived);

// Global variable to hold the compare value
volatile uint16_t compare_var = 750;

CY_ISR(ISR_UART_rx_handler)
{
    uint8_t byteReceived = UART_GetChar(); // Read received byte
    if (byteReceived) // Ensure a valid byte is received
    {
        handleByteReceived(byteReceived); // Handle the received byte
    }
}

void handleByteReceived(uint8_t byteReceived)
{
    switch(byteReceived)
    {
        case 'a': // Set PWM compare value to 1000
            compare_var = 750;
            UART_PutString("PWM set to 750.\r\n");
            break;
        case 's': // Set PWM compare value to 2700
            compare_var = 1700;
            UART_PutString("PWM set to 1700.\r\n");
            break;
        default:
            UART_PutString("Invalid input. Enter 'a' or 's'.\r\n");
            break;
    }
}

int main(void)
{
    CyGlobalIntEnable; /* Enable global interrupts. */
    
    isr_INT_StartEx(ISR_UART_rx_handler); // Start UART ISR
    UART_Start(); // Start UART communication
    
    UART_PutString("Enter 'a' to set PWM to 750.\r\n");
    UART_PutString("Enter 's' to set PWM to 1700.\r\n");

    PWM_Start(); // Start PWM
    
    for(;;)
    {
        // Continuously update the PWM compare value
        PWM_WriteCompare1(compare_var);
        PWM_WriteCompare2(compare_var);
    }
}

/* [] END OF FILE */
