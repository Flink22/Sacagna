#define F_CPU 16000000UL
#include <avr/io.h>
#include <avr/interrupt.h>
#include <math.h>
#include <util/delay.h>

#define n_mot 4
#define byteser 4

int readcomplete;
int setdrv = 1;

typedef struct {
	unsigned long curr;
	unsigned long old;
	unsigned long temp;
	unsigned long impulsi;
	int dir;
} def_readspeed;

typedef struct {
	char dir;
	int pwm;
} def_driver;

typedef struct {
	unsigned char byte;
} def_ser;

def_readspeed RSP[4];
def_driver DVR[4];
def_ser SER;

unsigned char Serial_Rx(void) {
	return UDR0;
}

void Serial_Tx(unsigned int data) {
	
	unsigned char temp[4];
	
	for (int k=0; k<4; k++){
		temp[k] = data%10;
		data = data / 10;
	}
	
	for (int k=0; k<4; k++){
		while (!(UCSR0A&(1<<UDRE0)));
		UDR0 = temp[k];
		_delay_us(1);
	}
	
	_delay_ms(1);
}

void init_gpio(){ //disattivo interrupt esterni e definisco entrate ed uscite

	DDRA = 0xF8;
	DDRJ = 0x8F;
	
	DDRD = 0x00;
	DDRH = 0x00;
	
	DDRL = 0x08;
	
	DDRE = 0x1A;
	DDRB = 0x68;
	
}

void init_intt(){ //definisco gli interrupt esterni e li attivo

	EICRA = 0xFF;
	EIMSK = (1<<INT0)|(1<<INT1)|(1<<INT2)|(1<<INT3);
	
	for(int i=0;i<4;i++){
		RSP[i].impulsi = 0;
	}

}

void init_pwm(){ //pwm 10 bit con t/c1 e t/c3

	TCCR1A = (1<<WGM10)|(1<<WGM11);
	TCCR1B = (0<<WGM12);
	TCCR1A |= (0<<COM1A0)|(1<<COM1A1);
	TCCR1A |= (0<<COM1B0)|(1<<COM1B1);

	TCCR3A = (1<<WGM30)|(1<<WGM31);
	TCCR3B = (0<<WGM32);
	TCCR3A |= (0<<COM3A0)|(1<<COM3A1);
	TCCR3A |= (0<<COM3B0)|(1<<COM3B1);

}

void start_pwm(){ //prescaler /64 per t/c1 e t/c3 + enable driver

	PORTA = (1<<PA5);
	PORTJ = (1<<PJ2);

	TCCR1B |= (1<<CS12)|(0<<CS11)|(0<<CS10);
	TCCR3B |= (1<<CS32)|(0<<CS31)|(0<<CS30);
	
	OCR1B = DVR[0].pwm * 1.1;
	OCR1A = DVR[1].pwm * 1.1;
	OCR3B = DVR[2].pwm;
	OCR3A = DVR[3].pwm;
	
	PORTJ = (1<<PJ2);
	PORTA = (1<<PA5);
	
	if(DVR[0].dir != 1){
		PORTJ |= (1<<PJ4)|(0<<PJ3);
		}else{
		PORTJ |= (0<<PJ4)|(1<<PJ3);
	}
	if(DVR[1].dir==1){
		PORTJ |= (0<<PJ1)|(1<<PJ0);
		}else{
		PORTJ |= (1<<PJ1)|(0<<PJ0);
	}
	if(DVR[2].dir==1){
		PORTA |= (0<<PA4)|(1<<PA3);
		}else{
		PORTA |= (1<<PA4)|(0<<PA3);
	}
	if(DVR[3].dir==1){
		PORTA |= (1<<PA7)|(0<<PA6);
		}else{
		PORTA |= (0<<PA7)|(1<<PA6);
	}
}

void init_serial(){
	
	UBRR0H = 0;
	UBRR0L = 1;
	UCSR0A = 0x80;
	UCSR0B = 0x98;
	UCSR0C = 0x06;
	
}

ISR(INT0_vect){
	RSP[0].impulsi++;
}

ISR(INT1_vect){
	RSP[1].impulsi++;
}

ISR(INT2_vect){
	RSP[3].impulsi++;
}

ISR(INT3_vect){
	RSP[2].impulsi++;
}

ISR(USART0_RX_vect){
	SER.byte = UDR0;
	readcomplete = 1;
	for(int i=0;i<4;i++){
		RSP[i].impulsi = 0;
	}	
	start_pwm();
}

int main(void){
	cli();
	
	init_pwm();
	init_gpio();
	init_serial();
	init_intt();

	for(int i=0;i<4;i++){
		DVR[i].pwm = 0;
		DVR[i].dir = 1;
	}
	
	start_pwm();
	
	sei();
	
	while(1) {
		if(SER.byte == 11){
			for(int i=0;i<4;i++){
				DVR[i].pwm = 500;
				DVR[0].dir = -1;
				DVR[1].dir = -1;
				DVR[2].dir = -1;
				DVR[3].dir = -1;
			}
			}else if(SER.byte == 12){
			for(int i=0;i<4;i++){
				DVR[i].pwm = 500;
				DVR[0].dir = 1;
				DVR[1].dir = 1;
				DVR[2].dir = -1;
				DVR[3].dir = -1;
			}
			}else if(SER.byte == 15){
			for(int i=0;i<4;i++){
				DVR[i].pwm = 500;
				DVR[0].dir = 1;
				DVR[1].dir = 1;
				DVR[2].dir = 1;
				DVR[3].dir = 1;
			}
			}else if(SER.byte == 14){
			for(int i=0;i<4;i++){
				DVR[i].pwm = 500;
				DVR[0].dir = -1;
				DVR[1].dir = -1;
				DVR[2].dir = 1;
				DVR[3].dir = 1;
			}
			}else if(SER.byte == 10){
			for(int i=0;i<4;i++){
				DVR[i].pwm = 0;
				RSP[i].impulsi = 0;
			}
		}
		if(readcomplete == 1){
			readcomplete = 0;
			start_pwm();
		}
		
		Serial_Tx(RSP[1].impulsi);
	}
}