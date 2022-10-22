#define F_CPU 16000000UL
#include <avr/io.h>
#include <avr/interrupt.h>
#include <math.h>

#define n_mot 4

volatile int mot_cursor;
volatile long int mot_curr[n_mot];
volatile long int mot_old[n_mot];
volatile long int mot_temp[n_mot];
volatile int mot_dir[n_mot];
volatile int pid_mot;
volatile float dist_travelled;
volatile float dist_temp;
volatile float speed;


void init_gpio();
void init_intt();
void init_timer4();
void init_pwm();
void start_pwm();
void init_pid();
void pid();

int main(void){

	init_gpio();
	init_intt();
	init_timer4();
	init_pwm();
	init_pid();
	
	int rpm_destra_A=0, rpm_sinistra_B=0;
	
	while(1) {
		
		rpm_destra_A = 2000000/(mot_curr[0] * 990) * 60;
		rpm_sinistra_B = 2000000/(mot_curr[1] * 990) * 60;
		
		if(rpm_destra_A> 15){
			PORTA= 0x01;
		} else{
			PORTA=0x00;
		}
		if(rpm_sinistra_B> 15){
			PORTA= 0x02;
			} else{
			PORTA=0x00;
		}
	}
}

void init_gpio(){ //disattivo interrupt esterni e definisco entrate ed uscite
	
	cli();
	
	DDRA = 0xFF;
	DDRB = 0xF0;
	DDRC = 0xFF;	
	
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

void pid(){
	
	if(pid_mot < 4){
		pid_mot = pid_mot + 1;
	} else{
		pid_mot = 0;
	}

	speed = 0;
	speed = 2000000/(mot_curr[pid_mot] * 990);

	if (speed > 0.1){
		
		dist_temp = (70 * M_PI) * speed * 0.032768;
		
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
	
	pid();
	
}
