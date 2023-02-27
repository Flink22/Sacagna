#define F_CPU 16000000UL				//non necessaria
#include <avr/io.h>					//necessaria per gestire PORT e PIN
#define acc 255						//le memorie byte che rappresentano un uno logico sono a 255
#include <avr/interrupt.h>				//necessaria per gestire sei()
#include <util/delay.h>

char byte;

unsigned char USART_Receive( void )
{
	/* Wait for data to be received */
	while ( !(UCSR0A & (1<<RXC0)) )
	;
	/* Get and return received data from buffer */
	return UDR0;
}


void Serial_Tx(int data) {
	while ( !( UCSR0A & (1<<UDRE0)) );
	UDR0 = data;
	
	_delay_ms(1);
	
}

int main(void)
{
	UBRR0H = 0;				//valore di UBRR0 che corrisponde alla baudrate 9600
	UBRR0L = 0;				
	UCSR0A = 0x00;				//RXC0 - TXC0 - UDRE0 - FE0 - DOR0 - UPE0 - U2X0 - MPCM0
	UCSR0B = 0b11000;				//Abilitata Tx RXCIE0 - TXCIE0 - UDRIE0 - RXEN0 - TXEN0 - UCSZ10 - RXB80 - TXB80
	UCSR0C = 0x06;				//Asincrono 8N1 UMSEL01 - UMSEL00 - UPM01 - UPM00 - USBS0 - UCSZ01 - UCSZ00 - UCPOL0


	sei();					//abilitazione generale degli interrupt
	while (1){
		byte = USART_Receive();
		Serial_Tx(byte);
		
	}
}
