#define F_CPU 16000000UL
#include <avr/io.h>
#include <avr/interrupt.h>
#include <math.h>
#include <util/delay.h>

#define n_mot 4

#define kp 140.0
#define ki 2.0
#define kd 50.0

int pid_mot = 0;

double speed[n_mot] = {0};
double speed_error = {0};
double old_error[n_mot] = {0};
double wanted_speed[n_mot] = {0};
double setspeed;

double proportional;
double integral[n_mot];
double derivative;
unsigned int correction;

double dist_travelled;
double dist_temp;

int setdrv = 1;

typedef struct {
	unsigned long int curr;
	unsigned long int old;
	unsigned long int temp;
	int dir;
} def_readspeed;

typedef struct {
	char dir;
	unsigned int pwm;
} def_driver;

def_readspeed RSP[4];
def_driver DVR[4];

void Serial_Tx(int data) {
	
	unsigned char temp[4];
	
	for (int k=0; k<4; k++){
		temp[k] = data%10;
		data = data / 10;
	}
	
	for (int k=0; k<4; k++){
		while ( !( UCSR0A & (1<<UDRE0)) );
		UDR0 = temp[k];
	}
	
	_delay_ms(1);
	
}

void init_gpio(){ //disattivo interrupt esterni e definisco entrate ed uscite

	cli();

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
		RSP[i].curr = 0;
		RSP[i].old = 0;
	}

}

void init_timer4(){ //faccio partire il timer 4 in normal mode (presc. /8) per velocità motori

	TCCR4A |= 0x00;
	TCCR4B |= (1<<CS41)|(0<<CS40);
	TCCR4C |= 0x00;

	TCNT4 = 0;

}

void init_pwm(){ //pwm 10 bit con t/c1 e t/c3

	TCCR1A |= (1<<WGM10)|(1<<WGM11);
	TCCR1B |= (0<<WGM12);
	TCCR1A |= (0<<COM1A0)|(1<<COM1A1);
	TCCR1A |= (0<<COM1B0)|(1<<COM1B1);

	TCCR3A |= (1<<WGM30)|(1<<WGM31);
	TCCR3B |= (0<<WGM32);
	TCCR3A |= (0<<COM3A0)|(1<<COM3A1);
	TCCR3A |= (0<<COM3B0)|(1<<COM3B1);

}

void start_pwm(){ //prescaler /1 per t/c1 e t/c3 + enable driver

	PORTA |= 0x20;
	PORTJ |= 0x04;

	TCCR1B |= (0<<CS12)|(1<<CS11)|(1<<CS10);
	TCCR3B |= (0<<CS32)|(1<<CS31)|(1<<CS30);

}

void init_serial(){
	
	UBRR0H = 0;
	UBRR0L = 1;
	UCSR0A = 0x00;
	UCSR0B = 0x08;
	UCSR0C = 0x06;
	
}

void init_pid(){ //Abilito t/c 0 per fare pid ogni intervallo di tempo (4000 Hz, quindi 1000 Hz a motore)

	TCCR0A = (1<<COM0A0)|(0<<COM0A1);
	TCCR0B = (1<<CS02)|(0<<CS01)|(0<<CS00);
	TIMSK0 = (1<<OCIE0A);
	
	OCR0A = 16;
	
	sei();
	
}

ISR(INT0_vect){
	
	int m=0;
	
	RSP[m].temp = TCNT4;

	if((PINH&0x08)!=0){
		RSP[m].dir = -1;
		} else{
		RSP[m].dir = 1;
	}
	
	RSP[m].curr = RSP[m].temp - RSP[m].old;

	RSP[m].old = RSP[m].temp;

}

ISR(INT1_vect){
	
	int m=1;
	
	RSP[m].temp = TCNT4;

	if((PINH&0x04)!=0){
		RSP[m].dir = -1;
		} else{
		RSP[m].dir = 1;
	}
	
	RSP[m].curr = RSP[m].temp - RSP[m].old;

	RSP[m].old = RSP[m].temp;
}

ISR(INT2_vect){
	
	int m=3;
	
	RSP[m].temp = TCNT4;

	if((PINH&0x01)!=0){
		RSP[m].dir = -1;
		} else{
		RSP[m].dir = 1;
	}
	
	RSP[m].curr = RSP[m].temp - RSP[m].old;

	RSP[m].old = RSP[m].temp;
}

ISR(INT3_vect){
	
	int m=2;
	
	RSP[m].temp = TCNT4;

	if((PINH&0x02)!=0){
		RSP[m].dir = -1;
		} else{
		RSP[m].dir = 1;
	}
	
	RSP[m].curr = RSP[m].temp - RSP[m].old;

	RSP[m].old = RSP[m].temp;
}


ISR(TIMER0_COMPA_vect){
	
	pid_mot ++;
	if(pid_mot >= 4){
		pid_mot = 0;
		setdrv = 1;
	}

	speed[pid_mot] = (((double)2000000.0) / (((double)RSP[pid_mot].curr) * 990.0));
	
	if (speed[pid_mot] < 0.1){
		speed[pid_mot] = 0;
	}
	else {
		speed[pid_mot] += speed[pid_mot] * -0.01;
	}
		
	if (speed[pid_mot] < 4){
		
		wanted_speed[pid_mot] = 1.2;
		setspeed = wanted_speed[pid_mot];
		
		proportional = 0;
		derivative = 0;
		correction = 0;
		
		if ((setspeed != 0) || ((setspeed == 0) && (speed[pid_mot] != 0))){
			
			speed_error = setspeed - speed[pid_mot];
			
			proportional = speed_error * kp;
			integral[pid_mot] += speed_error * ki;
			derivative = speed_error - old_error[pid_mot];
			
			old_error[pid_mot] = speed_error;
			
			if(proportional > 700)proportional = 700;	
			if(integral[pid_mot] > 5)integral[pid_mot] = 5;
			if(derivative > 200)derivative = 200;
			
			correction = proportional + integral[pid_mot] + (derivative * kd) + DVR[pid_mot].pwm;
			
			if(correction > 1023)correction = 1023;
			if(correction < 0)correction = 0;
			
			DVR[pid_mot].dir = -1;
			DVR[pid_mot].dir *= -1;
			DVR[pid_mot].pwm = correction;
			
		} else {
			DVR[pid_mot].pwm = 0;
		}
		
	}
	
}


int main(void){

	init_gpio();
	init_intt();
	init_timer4();
	init_pwm();
	init_pid();
	init_serial();

	for(int i=0;i<4;i++){
		integral[i] = 0;
		DVR[i].pwm = 0;
		DVR[i].dir = 1;
	}
	
	start_pwm();
	
	sei();
	
	while(1) {
		
		if(setdrv == 1){
			setdrv = 0;
			OCR1B = DVR[0].pwm;
			OCR1A = DVR[1].pwm;
			OCR3B = DVR[2].pwm;
			OCR3A = DVR[3].pwm;
			
			if(DVR[0].dir==1){
				PORTJ &= 0b111;PORTJ |= 0b10000;
			}else{
				PORTJ &= 0b111;PORTJ |= 0b1000;
			}
			if(DVR[1].dir==1){
				PORTJ &= 0b11100;PORTJ |= 0b1;
			}else{
				PORTJ &= 0b11100;PORTJ |= 0b10;
			}
			if(DVR[2].dir==1){
				PORTA &= 0b11100000;PORTA |= 0b01000;
			}else{
				PORTA &= 0b11100000;PORTA |= 0b10000;
			}			
			if(DVR[3].dir==1){
				PORTA &= 0b111000;PORTA |= 0b10000000;
			}else{
				PORTA &= 0b111000;PORTA |= 0b01000000;
			}
		}
		
	}

}
