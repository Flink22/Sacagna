#define F_CPU 16000000UL
#include <avr/io.h>
#include <avr/interrupt.h>
#include <math.h>

#define n_mot 4
#define kp 150
#define ki 2
#define kd 7

volatile int mot_cursor;

volatile int pid_mot;
volatile int error;
volatile int wanted_speed;
volatile int integral[n_mot];
volatile int derivative;
volatile long int old_error[n_mot];
volatile int correction;

volatile long int mot_curr[n_mot];
volatile long int mot_old[n_mot];
volatile long int mot_temp[n_mot];
volatile int mot_dir[n_mot];

volatile float dist_travelled;
volatile float dist_temp;
volatile float speed;

volatile int driver[n_mot][4];

volatile int i;

void init_gpio();
void init_intt();
void init_timer4();
void init_pwm();
void start_pwm();
void init_pid();
void driver_set();

int main(void){

	init_gpio();
	init_intt();
	init_timer4();
	init_pwm();
	init_pid();
	
	for(i=0;i<4;i++){
		integral[i] = 0;
	}
	
	start_pwm();

	while(1) {
		PORTD = 0b110000;
		OCR3B = 1023;
	}

}

void init_gpio(){ //disattivo interrupt esterni e definisco entrate ed uscite

	cli();

	DDRA = 0xF8;
	DDRJ = 0x8F;
	
	DDRD = 0x0F;
	DDRH = 0x0F;
	
	DDRL = 0x08;
	
	DDRE = 0x1A;
	DDRB = 0x68;

}

void init_intt(){ //definisco gli interrupt esterni e li attivo

	EICRA = 0xFF;
	EIMSK = (1<<INT0)|(1<<INT1)|(1<<INT2)|(1<<INT3);
	sei();

}

void init_timer4(){ //faccio partire il timer 4 in normal mode (presc. /8) per velocità motori

	TCCR4A = 0x00;
	TCCR4B = (1<<CS41);
	TCCR4C = 0x00;

	TCNT4 = 0;

}

void init_pwm(){ //pwm 10 bit phase corrected con t/c1 e t/c3

	TCCR1A |= (1<<WGM10)|(1<<WGM11);
	TCCR1A |= (0<<COM1A0)|(1<<COM1A1);
	TCCR1A |= (0<<COM1B0)|(1<<COM1B1);

	TCCR3A |= (1<<WGM30)|(1<<WGM31);
	TCCR3A |= (0<<COM3A0)|(1<<COM3A1);
	TCCR3A |= (0<<COM3B0)|(1<<COM3B1);

}

void start_pwm(){ //prescaler /64 per t/c1 e t/c3 + enable driver

	PORTC |= 0xC0;

	TCCR1B |= (0<<CS12)|(1<<CS11)|(1<<CS10);
	TCCR3B |= (0<<CS32)|(1<<CS31)|(1<<CS30);

}

void init_pid(){ //Abilito t/c 0 per fare pid ogni intervallo di tempo ()

	TCCR0A = (1<<COM0A1)|(1<<COM0A0);
	TCCR0B = (1<<CS00)|(0<<CS01)|(0<<CS02); //prescaler /256

}

void driver_set(){
	
	switch(pid_mot){
		
		case 0:
			if(driver[0][0]<0){
				driver[0][0] = driver[0][0] * -1;
				PORTJ &= 0b111;
				PORTJ |= 0b10000;
			}else{
				PORTJ &= 0b111;
				PORTJ |= 0b1000;
			}
			OCR1B = driver[0][0];
			break;
			
		case 1:
		if(driver[1][0]<0){
			driver[1][0] = driver[1][0] * -1;
			PORTJ &= 0b11100;
			PORTJ |= 0b1;
			}else{
			PORTJ &= 0b11100;
			PORTJ |= 0b10;
		}
		OCR1A = driver[1][0];
		break;
		
		case 2:
		if(driver[2][0]<0){
			driver[2][0] = driver[2][0] * -1;
			PORTA &= 0b11100000;
			PORTA |= 0b1000;
			}else{
			PORTA &= 0b11100000;
			PORTA |= 0b10000;
		}
		OCR3B = driver[2][0];
		break;
		
		case 3:
		if(driver[3][0]<0){
			driver[3][0] = driver[3][0] * -1;
			PORTA &= 0b111000;
			PORTA |= 0b10000000;
			}else{
			PORTA &= 0b111000;
			PORTA |= 0b1000000;
		}
		OCR3A = driver[3][0];
		break;
		
	}
	
}

ISR(INT0_vect){

	mot_cursor = 0;
	mot_temp[mot_cursor] = TCNT4;

	if((PORTB&0x01)!=0){
		mot_dir[mot_cursor] = 1;
		} else{
		mot_dir[mot_cursor] = -1;
	}

	if(mot_temp[mot_cursor] > mot_old[mot_cursor]){
		mot_curr[mot_cursor] = mot_temp[mot_cursor] - mot_old[mot_cursor];
	}

	if(mot_temp[mot_cursor] < mot_old[mot_cursor]){
		mot_old[mot_cursor] = mot_old[mot_cursor] - 65535;
		mot_curr[mot_cursor] = mot_temp[mot_cursor] - mot_old[mot_cursor];
	}

	mot_old[mot_cursor] = mot_temp[mot_cursor];

}

ISR(INT1_vect){

	mot_cursor = 1;
	mot_temp[mot_cursor] = TCNT4;

	if((PORTB&0x02)!=0){
		mot_dir[mot_cursor] = 1;
		} else{
		mot_dir[mot_cursor] = -1;
	}

	if(mot_temp[mot_cursor] > mot_old[mot_cursor]){
		mot_curr[mot_cursor] = mot_temp[mot_cursor] - mot_old[mot_cursor];
	}

	if(mot_temp[mot_cursor] < mot_old[mot_cursor]){
		mot_old[mot_cursor] = mot_old[mot_cursor] - 65535;
		mot_curr[mot_cursor] = mot_temp[mot_cursor] - mot_old[mot_cursor];
	}

	mot_old[mot_cursor] = mot_temp[mot_cursor];

}

ISR(INT2_vect){

	mot_cursor = 2;
	mot_temp[mot_cursor] = TCNT4;

	if((PORTB&0x04)!=0){
		mot_dir[mot_cursor] = 1;
		} else{
		mot_dir[mot_cursor] = -1;
	}

	if(mot_temp[mot_cursor] > mot_old[mot_cursor]){
		mot_curr[mot_cursor] = mot_temp[mot_cursor] - mot_old[mot_cursor];
	}

	if(mot_temp[mot_cursor] < mot_old[mot_cursor]){
		mot_old[mot_cursor] = mot_old[mot_cursor] - 65535;
		mot_curr[mot_cursor] = mot_temp[mot_cursor] - mot_old[mot_cursor];
	}

	mot_old[mot_cursor] = mot_temp[mot_cursor];

}

ISR(INT3_vect){

	mot_cursor = 3;
	mot_temp[mot_cursor] = TCNT4;

	if((PORTB&0x08)!=0){
		mot_dir[mot_cursor] = 1;
		} else{
		mot_dir[mot_cursor] = -1;
	}

	if(mot_temp[mot_cursor] > mot_old[mot_cursor]){
		mot_curr[mot_cursor] = mot_temp[mot_cursor] - mot_old[mot_cursor];
	}

	if(mot_temp[mot_cursor] < mot_old[mot_cursor]){
		mot_old[mot_cursor] = mot_old[mot_cursor] - 65535;
		mot_curr[mot_cursor] = mot_temp[mot_cursor] - mot_old[mot_cursor];
	}

	mot_old[mot_cursor] = mot_temp[mot_cursor];

}

ISR(TIMER0_COMPA_vect){

	if(pid_mot < 4){
		pid_mot = pid_mot + 1;
		} else{
		pid_mot = 0;
	}

	speed = 0;
	speed = 2000000/(mot_curr[pid_mot] * 990) * mot_dir[pid_mot];

	if (speed > 0.1){

		dist_temp = (70 * M_PI) * speed * 0.032768;

	}

	wanted_speed = 1;

	error = wanted_speed - speed;
	integral[pid_mot] += ki * error;
	derivative = (error - old_error[pid_mot]) * kd;
	old_error[pid_mot] = error;

	correction = error * kp + derivative + integral[pid_mot];
	if(correction > 1023)
	correction = 1023;
	if(correction < 1023)
	correction = -1023;
	
}
