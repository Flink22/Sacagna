#include <stdio.h>
#include <math.h>
#include "pico/stdlib.h"
#include "hardware/pwm.h"
#include "hardware/gpio.h"
#include "hardware/uart.h"
#include "hardware/irq.h"
#include "hardware/clocks.h"

#define PLL_SYS_KHZ (200 * 1000)

#define UART_ID uart0
#define BAUD_RATE 1000000
#define DATA_BITS 8
#define STOP_BITS 1
#define PARITY    UART_PARITY_NONE
#define UART_TX_PIN 0
#define UART_RX_PIN 1

#define n_mot 4

#define kp 50000.0
#define ki 20000.0
#define kd 0.0
#define diametro 69.0

#define Plim 25000.0
#define Ilim 10000.0
#define Dlim 0.0

typedef struct {
    volatile uint IN1;
    volatile uint IN2;
    volatile uint PWM;
    volatile int PWM_CHAN;
    volatile uint slice;
    volatile int corr;
} def_driver;

typedef struct {
    volatile uint IN1;
    volatile uint IN2;
} def_encoder;

typedef struct {
	volatile uint32_t curr;
	volatile uint32_t old;
	volatile uint32_t temp;
	volatile uint impulsi;
	volatile int dir;
    def_encoder ENC;
} def_readspeed;

typedef struct {
	int mot;
	double P;
	double I[n_mot];
	double D;
	double correction;
    int pwm[n_mot];
} def_pid;

typedef struct {
    unsigned char M1;
    unsigned char M2;
    unsigned char M3;
    unsigned char M4;
    unsigned char SERVO;
} def_ser;

def_driver DVR[n_mot];
def_readspeed RSP[n_mot];
def_ser SER;
def_pid PiD;

volatile int EN_MOT;
volatile int SERVO_PIN_PWM;
volatile int SERVO_PWM = 1250;
volatile uint slice_ser;
volatile char read;
volatile int readcomplete;

volatile double speed[n_mot] = {0};
volatile double speed_error = 0;
volatile double old_error[n_mot] = {0};
volatile double wanted_speed[n_mot] = {0};
volatile signed int wanted_dir[n_mot] = {0};

void Serial_RX(void) {
    read = uart_getc(uart0);
    readcomplete = 1;
}

void Serial_TX(uint data){
    unsigned char temp[4];
	sleep_us(100);
	for (int k=0; k<4; k++){
		temp[k] = data%10;
		data = data / 10;
	}
	
	for (int k=0; k<4; k++){
		uart_putc(UART_ID, temp[k]);
		sleep_us(1);
	}
    sleep_us(100);
}

void var_setup() {
    DVR[0].PWM = 2;
    DVR[1].PWM = 7;
    DVR[2].PWM = 8;
    DVR[3].PWM = 13;

    DVR[0].IN1 = 3;
    DVR[1].IN1 = 5;
    DVR[2].IN1 = 10;
    DVR[3].IN1 = 12;

    DVR[0].IN2 = 4;
    DVR[1].IN2 = 6;
    DVR[2].IN2 = 9;
    DVR[3].IN2 = 11;

    RSP[0].ENC.IN1 = 26;
    RSP[1].ENC.IN1 = 28;
    RSP[2].ENC.IN1 = 18;
    RSP[3].ENC.IN1 = 20;
    
    RSP[0].ENC.IN2 = 22;
    RSP[1].ENC.IN2 = 27;
    RSP[2].ENC.IN2 = 19;
    RSP[3].ENC.IN2 = 21;

    EN_MOT = 14;
    SERVO_PIN_PWM = 15;
    SERVO_PWM = 0;

    slice_ser = pwm_gpio_to_slice_num(14);
    DVR[0].slice = pwm_gpio_to_slice_num(2);
    DVR[1].slice = pwm_gpio_to_slice_num(6);
    DVR[2].slice = pwm_gpio_to_slice_num(8);
    DVR[3].slice = pwm_gpio_to_slice_num(12);

    DVR[0].PWM_CHAN = 0;
    DVR[1].PWM_CHAN = 1;
    DVR[2].PWM_CHAN = 0;
    DVR[3].PWM_CHAN = 1;

    PiD.I[0] = 0;
    PiD.I[1] = 0;
    PiD.I[2] = 0;
    PiD.I[3] = 0;

    RSP[0].curr = 50000;
    RSP[1].curr = 50000;
    RSP[2].curr = 50000;
    RSP[3].curr = 50000;

    RSP[0].old = 0;
    RSP[1].old = 0;
    RSP[2].old = 0;
    RSP[3].old = 0;

    RSP[0].impulsi = 0;
    RSP[1].impulsi = 0;
    RSP[2].impulsi = 0;
    RSP[3].impulsi = 0;

    DVR[0].corr = 1;
    DVR[1].corr = 1;
    DVR[2].corr = -1;
    DVR[3].corr = -1;
}

int serv_getang(int ang) {
    int duty = ((ang / 18.0) * 125.0) + 1250;
    return duty;
}

void driver_set(int mot, int dir, int pwm) {
    dir = dir * DVR[mot].corr;
    if (dir == 1){
        gpio_put(DVR[mot].IN1, 1);
        gpio_put(DVR[mot].IN2, 0);
    }else if (dir == -1){
        gpio_put(DVR[mot].IN1, 0);
        gpio_put(DVR[mot].IN2, 1);
    }else if (dir == 0){ //BRAKE
        pwm_set_chan_level(DVR[mot].slice, DVR[mot].PWM_CHAN, 0);
        gpio_put(DVR[mot].IN1, 1);
        gpio_put(DVR[mot].IN2, 1);
    }else if (dir == 2){ //OFF
        gpio_put(DVR[mot].IN1, 0);
        gpio_put(DVR[mot].IN2, 0);
    }
    pwm_set_chan_level(DVR[mot].slice, DVR[mot].PWM_CHAN, pwm);
}

void mot_setup() {
    gpio_set_function(SERVO_PIN_PWM, GPIO_FUNC_PWM);

    gpio_init(EN_MOT);
    gpio_set_dir(EN_MOT, GPIO_OUT);
    gpio_put(EN_MOT, 1);

    for(int i=0;i<4;i++){
        gpio_set_function(DVR[i].PWM, GPIO_FUNC_PWM);

        gpio_init(DVR[i].IN1);
        gpio_set_dir(DVR[i].IN1, GPIO_OUT);
        gpio_put(DVR[i].IN1, 0);

        gpio_init(DVR[i].IN2);
        gpio_set_dir(DVR[i].IN2, GPIO_OUT);
        gpio_put(DVR[i].IN2, 0);
    }

    pwm_set_clkdiv(slice_ser, 100.0);
    pwm_set_wrap(slice_ser, 25000);
    pwm_set_chan_level(slice_ser, PWM_CHAN_B, SERVO_PWM);
    pwm_set_enabled(slice_ser, true);

    for(int i=0;i<4;i++){
        pwm_set_clkdiv(DVR[i].slice, 100.0);
        pwm_set_wrap(DVR[i].slice, 25000);
        pwm_set_chan_level(DVR[i].slice, DVR[i].PWM_CHAN, 10);
        pwm_set_enabled(DVR[i].slice, true);
    }

}

void enc_interrupt(uint gpio, uint32_t events){
    int m;

	if(gpio==RSP[0].ENC.IN1)m=0;
    if(gpio==RSP[1].ENC.IN1)m=1;
    if(gpio==RSP[2].ENC.IN1)m=2;
    if(gpio==RSP[3].ENC.IN1)m=3;

    RSP[m].impulsi++;

    RSP[m].temp = timer_hw->timelr;
    RSP[m].curr = RSP[m].temp - RSP[m].old;
    RSP[m].old = RSP[m].temp;
}

bool PID(struct repeating_timer *t) {

    PiD.mot ++;
	if(PiD.mot > 3){
		PiD.mot = 0;
	}
	
	speed[PiD.mot] = (((double)1000000.0) / (((double)RSP[PiD.mot].curr) * 990.0));

    if (speed[PiD.mot] > 2.0)speed[PiD.mot] = 0.0;
	
	if (speed[PiD.mot] < 2.0){
		
		PiD.P = 0;
		PiD.D = 0;
		PiD.correction = 0;
		
		if (wanted_speed[PiD.mot]  != 0){
			
			speed_error = wanted_speed[PiD.mot] - speed[PiD.mot];
			
			PiD.P = speed_error * kp;
			PiD.I[PiD.mot] += speed_error * ki;
			
			old_error[PiD.mot] = speed_error;
			
			if(PiD.P > Plim) PiD.P = Plim;
			if(PiD.P < -Plim) PiD.P = -Plim;
			if(PiD.I[PiD.mot] > Ilim) PiD.I[PiD.mot] = Ilim;
			if(PiD.I[PiD.mot] < -Ilim) PiD.I[PiD.mot] = -Ilim;
			
			PiD.correction = PiD.P + PiD.I[PiD.mot];
			
			if(PiD.correction > 25000)PiD.correction = 25000;
			if(PiD.correction < 0)PiD.correction = 0;

            PiD.pwm[PiD.mot] = PiD.correction;

            driver_set(PiD.mot, wanted_dir[PiD.mot], PiD.pwm[PiD.mot]);
	    } else{
            driver_set(PiD.mot, 0, 0);
        }
    }
    return true;
}

void extint_setup() {
	gpio_set_input_enabled(RSP[0].ENC.IN1, true);
    gpio_set_input_enabled(RSP[1].ENC.IN1, true);

    gpio_pull_up(RSP[0].ENC.IN1);
    gpio_pull_up(RSP[1].ENC.IN1);
    gpio_pull_up(RSP[2].ENC.IN1);
    gpio_pull_up(RSP[3].ENC.IN1);
    
    gpio_set_irq_enabled_with_callback(RSP[0].ENC.IN1, GPIO_IRQ_EDGE_RISE, true, &enc_interrupt);
    gpio_set_irq_enabled(RSP[1].ENC.IN1, GPIO_IRQ_EDGE_RISE, true);
    gpio_set_irq_enabled(RSP[2].ENC.IN1, GPIO_IRQ_EDGE_RISE, true);
    gpio_set_irq_enabled(RSP[3].ENC.IN1, GPIO_IRQ_EDGE_RISE, true);
}

void uart_setup() {
    uart_init(UART_ID, 2400);
    gpio_set_function(UART_TX_PIN, GPIO_FUNC_UART);
    gpio_set_function(UART_RX_PIN, GPIO_FUNC_UART);
    int __unused actual = uart_set_baudrate(UART_ID, BAUD_RATE);
    uart_set_hw_flow(UART_ID, false, false);
    uart_set_format(UART_ID, DATA_BITS, STOP_BITS, PARITY);
    uart_set_fifo_enabled(UART_ID, false);
    int UART_IRQ = UART_ID == uart0 ? UART0_IRQ : UART1_IRQ;
    irq_set_exclusive_handler(UART_IRQ, Serial_RX);
    irq_set_enabled(UART_IRQ, true);
    uart_set_irq_enables(UART_ID, true, false);
    uart_puts(UART_ID, "1");
}

int main() {
    set_sys_clock_khz(PLL_SYS_KHZ, true);
    stdio_init_all();
    var_setup();
    mot_setup();
    extint_setup();
    uart_setup();
    
    SERVO_PWM = serv_getang(0);
    pwm_set_chan_level(slice_ser, PWM_CHAN_B, SERVO_PWM);

    struct repeating_timer timer;
    add_repeating_timer_us(-500, PID, NULL, &timer);

    while(1){

        Serial_TX(RSP[2].impulsi);

        if(readcomplete == 1){

            readcomplete = 0;
            for(int i=0;i<4;i++){
                RSP[i].impulsi = 0;
                wanted_speed[i] = 0.8;
            }

            if(read == 11){
                for(int i=0;i<4;i++){
                    wanted_speed[i] = 1.0;
                    wanted_dir[i] = 1;
                }
            }else if(read == 12){
                wanted_dir[0] = -1;
                wanted_dir[1] = -1;
                wanted_dir[2] = 1;
                wanted_dir[3] = 1;
            }else if(read == 13){
                for(int i=0;i<4;i++){
                    wanted_speed[i] = 0.8;
                    wanted_dir[i] = -1;
                }
            }else if(read == 14){
                wanted_dir[0] = 1;
                wanted_dir[1] = 1;
                wanted_dir[2] = -1;
                wanted_dir[3] = -1;
            }else if(read == 10){
                for(int i=0;i<4;i++){
                    wanted_speed[i] = 0.0;
                    wanted_dir[i] = 0;
                }
            }
            for(int i=0;i<4;i++){
                RSP[i].impulsi = 0;
            }
        }

    }    
}
