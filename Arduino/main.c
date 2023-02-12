#define F_CPU 16000000UL
#include <avr/io.h>
#include <avr/interrupt.h>
#include <math.h>
#include <util/delay.h>

#define n_mot 4

#define kp 150.0
#define ki 2.0
#define kd 7.0

int mot_cursor = 0;

int pid_mot = 0;

float speed_error;
float wanted_speed[n_mot];
float integral[n_mot];
float derivative;
float proportional;
long int old_error[n_mot];
long int correction;
float speed[n_mot];

unsigned long int mot_curr[n_mot];
unsigned long int mot_old[n_mot];
unsigned long int mot_temp[n_mot];
int mot_dir[n_mot];

float dist_travelled;
float dist_temp;

int driver[n_mot][4];

int i;

void init_gpio();
void init_intt();
void init_timer4();
void init_pwm();
void start_pwm();
void init_pid();
void init_serial();
void driver_set();

unsigned char a = 0;
unsigned char temp[3];

void Serial_Tx(int data) {

	if(data < 0)
	data *= -1;
	
	if (data>99) {
		for (int k=0; k<3; k++){
			temp[k] = data%10;
			data = data / 10;
		}
		}else if(data>9) {
		for (int k=0; k<2; k++){
			temp[k] = data%10;
			data = data / 10;
		}
		temp[2] = 0;
		}else {
		temp[0] = data;
		temp[1] = 0;
		temp[2] = 0;
	}
	
	for (int k=0; k<3; k++){
		while ( !( UCSR0A & (1<<UDRE0)) );
		UDR0 = temp[k];
	}
	
	_delay_ms(1);
	
}

int main(void){

	init_gpio();
	init_intt();
	init_timer4();
	init_pwm();
	init_pid();
	init_serial();
	
	sei();
	
	for(i=0;i<4;i++){
		integral[i] = 0;
	}
	
	start_pwm();
	
	while(1) {
	}

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

}

void init_timer4(){ //faccio partire il timer 4 in normal mode (presc. /8) per velocità motori

	TCCR4A |= 0x00;
	TCCR4B |= (1<<CS41)|(1<<CS40);
	TCCR4C |= 0x00;

	TCNT4 = 0;

}

void init_pwm(){ //pwm 10 bit phase corrected con t/c1 e t/c3

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

	TCCR1B |= (0<<CS12)|(0<<CS11)|(1<<CS10);
	TCCR3B |= (0<<CS32)|(0<<CS31)|(1<<CS30);

}

void init_serial(){
	
	UBRR0H = 0;
	UBRR0L = 1;
	UCSR0A = 0x00;
	UCSR0B = 0x08;
	UCSR0C = 0x06;
	
}

void init_pid(){ //Abilito t/c 0 per fare pid ogni intervallo di tempo (400 Hz, quindi 100 Hz a motore)

	TCCR0A = (1<<COM0A0)|(0<<COM0A1);
	TCCR0B = (1<<CS02)|(0<<CS01)|(0<<CS00);
	TIMSK0 = (1<<OCIE0A);
	
	OCR0A = 156;
	
	sei();
	
}

ISR(INT0_vect){
	
	mot_temp[0] = TCNT4;

	if((PINH&0x08)!=0){
		mot_dir[0] = -1;
		} else{
		mot_dir[0] = 1;
	}

	if(mot_temp[0] >= mot_old[0]){
		mot_curr[0] = mot_temp[0] - mot_old[0];
		} else{
		mot_old[0] = mot_old[0] - 65535;
		mot_curr[0] = mot_temp[0] - mot_old[0];
	}

	mot_old[0] = mot_temp[0];

}

ISR(INT1_vect){

	mot_temp[1] = TCNT4;

	if((PINH&0x04)!=0){
		mot_dir[1] = -1;
		} else{
		mot_dir[1] = 1;
	}

	if(mot_temp[1] >= mot_old[1]){
		mot_curr[1] = mot_temp[1] - mot_old[1];
		} else{
		mot_old[1] = mot_old[1] - 65535;
		mot_curr[1] = mot_temp[1] - mot_old[1];
	}

	mot_old[1] = mot_temp[1];

}

ISR(INT2_vect){

	mot_temp[2] = TCNT4;

	if((PINH&0x01)!=0){
		mot_dir[2] = -1;
		} else{
		mot_dir[2] = 1;
	}

	if(mot_temp[2] >= mot_old[2]){
		mot_curr[2] = mot_temp[2] - mot_old[2];
		} else{
		mot_old[2] = mot_old[2] - 65535;
		mot_curr[2] = mot_temp[2] - mot_old[2];
	}

	mot_old[2] = mot_temp[2];

}

ISR(INT3_vect){

	mot_temp[3] = TCNT4;

	if((PINH&0x02)!=0){
		mot_dir[3] = -1;
		} else{
		mot_dir[3] = 1;
	}

	if(mot_temp[3] >= mot_old[3]){
		mot_curr[3] = mot_temp[3] - mot_old[3];
		} else{
		mot_old[3] = mot_old[3] - 65535;
		mot_curr[3] = mot_temp[3] - mot_old[3];
	}

	mot_old[3] = mot_temp[3];

}

ISR(TIMER0_COMPA_vect){
	
	pid_mot ++;
	if(pid_mot >= 4)pid_mot = 0;

	speed[pid_mot] = (((double)(2000000)))/(((double)mot_curr[pid_mot]) * 990);
	
	if (speed[pid_mot] < 3){
	
		speed[pid_mot] = (int)speed[pid_mot];
		Serial_Tx(speed[pid_mot]);
	
		wanted_speed[pid_mot] = 200;
	
		proportional = 0;
		derivative = 0;
	
		if (speed[pid_mot] < 150){

			speed_error = wanted_speed[pid_mot] - speed[pid_mot];
			proportional = speed_error * kp;
			integral[pid_mot] += speed_error * ki;
			derivative = (speed_error - old_error[pid_mot]) * ki;
			old_error[pid_mot] = speed_error;
		
			if(proportional >= 500)proportional = 500;
			if(proportional <= -500)proportional = -500;
		
			if(integral[pid_mot] >= 0.2)integral[pid_mot] = 0.2;
			if(integral[pid_mot] <= -0.2)integral[pid_mot] = -0.2;
		
			if(derivative >= 200)derivative = 200;
			if(derivative <= -200)derivative = -200;

			correction = proportional + derivative + integral[pid_mot];
		
			if(correction >= 1023)correction = 1023;
			if(correction <= 0)correction = 0;

			driver[pid_mot][0] = correction;
		
		}
	}
	
	if(pid_mot == 3){
		driver_set();
	}
	
}

void driver_set(){

	if(driver[0][0]<0){
		PORTJ &= 0b111;
		PORTJ |= 0b10000;
		OCR1B = (driver[0][0] * -1);
		}else{
		PORTJ &= 0b111;
		PORTJ |= 0b1000;
		OCR1B = driver[0][0];
	}
	
	if(driver[1][0]<0){
		PORTJ &= 0b11100;
		PORTJ |= 0b1;
		OCR1A = (driver[1][0] * -1);
		}else{
		PORTJ &= 0b11100;
		PORTJ |= 0b10;
		OCR1A = driver[1][0];
	}
	
	if(driver[2][0]<0){
		PORTA &= 0b11100000;
		PORTA |= 0b01000;
		OCR3B = (driver[2][0] * -1);
		}else{
		PORTA &= 0b11100000;
		PORTA |= 0b10000;
		OCR3B = driver[2][0];
	}
	
	if(driver[3][0]<0){
		PORTA &= 0b111000;
		PORTA |= 0b10000000;
		OCR3A = (driver[3][0] * -1);
		}else{
		PORTA &= 0b111000;
		PORTA |= 0b01000000;
		OCR3A = driver[3][0];
	}

}
