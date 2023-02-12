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

typedef struct {
	unsigned int curr;
	unsigned int old;
	unsigned int temp;
	int dir;
} def_readspeed;

typedef struct {
	double speed;
	double err;
	double old_err;
	double wanted;
	double travelled;
} def_speed;

typedef struct {
	unsigned int pwm;
	int dir;
} def_driver;

typedef struct {
	double I;
	double D;
	double P;
	int cor;
} def_pid;

typedef struct {
	def_readspeed rs;
	def_speed sp;
	def_driver dr;
	def_pid pid;
} def_mott;

typedef struct {
	def_mott M[n_mot];
} def_mot;


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
	
	def_mot MOT;
	init_gpio();
	init_intt();
	init_timer4();
	init_pwm();
	init_pid();
	init_serial();
	
	sei();
	
	for(i=0;i<4;i++){
		MOT.M[i].pid.I = 0;
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
	
	def_mot MOT;
	
	MOT.M[0].rs.temp = TCNT4;

	if((PINH&0x08)!=0){
		MOT.M[0].rs.dir = -1;
	} else{
		MOT.M[0].rs.dir = 1;
	}
	
	MOT.M[0].rs.curr = MOT.M[0].rs.temp - MOT.M[0].rs.old;
	MOT.M[0].rs.old = MOT.M[0].rs.temp;

}

ISR(INT1_vect){

	def_mot MOT;
	
	MOT.M[1].rs.temp = TCNT4;

	if((PINH&0x04)!=0){
		MOT.M[1].rs.dir = -1;
		} else{
		MOT.M[1].rs.dir = 1;
	}
	
	MOT.M[1].rs.curr = MOT.M[1].rs.temp - MOT.M[1].rs.old;
	MOT.M[1].rs.old = MOT.M[1].rs.temp;

}

ISR(INT2_vect){

	def_mot MOT;
	
	MOT.M[2].rs.temp = TCNT4;

	if((PINH&0x01)!=0){
		MOT.M[2].rs.dir = -1;
	} else{
		MOT.M[2].rs.dir = 1;
	}
	
	MOT.M[2].rs.curr = MOT.M[2].rs.temp - MOT.M[2].rs.old;
	MOT.M[2].rs.old = MOT.M[2].rs.temp;

}

ISR(INT3_vect){

	def_mot MOT;
	
	MOT.M[3].rs.temp = TCNT4;

	if((PINH&0x02)!=0){
		MOT.M[3].rs.dir = -1;
	} else{
		MOT.M[3].rs.dir = 1;
	}
	
	MOT.M[3].rs.curr = MOT.M[3].rs.temp - MOT.M[3].rs.old;
	MOT.M[3].rs.old = MOT.M[3].rs.temp;

}

ISR(TIMER0_COMPA_vect){
	
	def_mot MOT;
	
	pid_mot ++;
	if(pid_mot >= 4)pid_mot = 0;
	
	MOT.M[pid_mot].sp.speed = (((double)(2000000)))/(((double)MOT.M[pid_mot].rs.curr) * 990);
	
	if (MOT.M[pid_mot].sp.speed < 3){
		
		Serial_Tx(MOT.M[pid_mot].sp.speed);
		MOT.M[pid_mot].sp.wanted = 2;
		
		if (MOT.M[pid_mot].sp.speed < 150){

			MOT.M[pid_mot].sp.err = MOT.M[pid_mot].sp.wanted - MOT.M[pid_mot].sp.speed;
			
			MOT.M[pid_mot].pid.P = MOT.M[pid_mot].sp.err * kp;
			MOT.M[pid_mot].pid.I += MOT.M[pid_mot].sp.err * ki;
			MOT.M[pid_mot].pid.D = (MOT.M[pid_mot].sp.err - MOT.M[pid_mot].sp.old_err) * ki;
			
			MOT.M[pid_mot].sp.old_err = MOT.M[pid_mot].sp.err;
		
			if(MOT.M[pid_mot].pid.P >= 500)MOT.M[pid_mot].pid.P = 500;
			if(MOT.M[pid_mot].pid.P <= 0)MOT.M[pid_mot].pid.P = 0;
		
			if(MOT.M[pid_mot].pid.I >= 0.2)MOT.M[pid_mot].pid.I = 0.2;
			if(MOT.M[pid_mot].pid.I <= 0)MOT.M[pid_mot].pid.I = 0;
		
			if(MOT.M[pid_mot].pid.D >= 200)MOT.M[pid_mot].pid.D = 200;
			if(MOT.M[pid_mot].pid.D <= 0)MOT.M[pid_mot].pid.D = 0;

			MOT.M[pid_mot].pid.cor = MOT.M[pid_mot].pid.P + MOT.M[pid_mot].pid.D + MOT.M[pid_mot].pid.I;
		
			if(MOT.M[pid_mot].pid.cor >= 1023)MOT.M[pid_mot].pid.cor = 1023;
			if(MOT.M[pid_mot].pid.cor <= 0)MOT.M[pid_mot].pid.cor = 0;

			MOT.M[pid_mot].dr.pwm = MOT.M[pid_mot].pid.cor;
		
		}
	}
	
	if(pid_mot == 3){
		driver_set();
	}
	
}

void driver_set(){
	
	def_mot MOT;

	if(MOT.M[0].dr.dir < 0){
		PORTJ &= 0b111;
		PORTJ |= 0b10000;
	}else{
		PORTJ &= 0b111;
		PORTJ |= 0b1000;
	}
	
	if(MOT.M[1].dr.dir < 0){
		PORTJ &= 0b11100;
		PORTJ |= 0b1;
	}else{
		PORTJ &= 0b11100;
		PORTJ |= 0b10;
	}
	
	if(MOT.M[2].dr.dir < 0){
		PORTA &= 0b11100000;
		PORTA |= 0b01000;
	}else{
		PORTA &= 0b11100000;
		PORTA |= 0b10000;
	}
	
	if(MOT.M[3].dr.dir < 0){
		PORTA &= 0b111000;
		PORTA |= 0b10000000;
	}else{
		PORTA &= 0b111000;
		PORTA |= 0b01000000;
	}
	
	OCR1B = MOT.M[0].dr.pwm;
	OCR1A = MOT.M[1].dr.pwm;
	OCR3B = MOT.M[2].dr.pwm;
	OCR3A = MOT.M[3].dr.pwm;

}
