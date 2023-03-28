#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/pwm.h"
#include "hardware/gpio.h"

typedef struct {
    volatile int IN1;
    volatile int IN2;
    volatile int PWM;
    volatile int PWM_CHAN;
    volatile uint slice;
} def_set;

typedef struct {
	volatile char dir;
	volatile int pwm;
    volatile def_set SET;
} def_driver;

typedef struct {
	unsigned long curr;
	unsigned long old;
	unsigned long temp;
	unsigned long impulsi;
	int dir;
} def_readspeed;

def_driver DVR[4];

volatile int EN_MOT;
volatile int SERVO_PIN_PWM;
volatile int SERVO_PWM = 1250;
volatile uint slice_ser;

void var_setup() {
    DVR[0].SET.PWM = 2;
    DVR[1].SET.PWM = 7;
    DVR[2].SET.PWM = 8;
    DVR[3].SET.PWM = 13;

    DVR[0].SET.IN1 = 3;
    DVR[1].SET.IN1 = 5;
    DVR[2].SET.IN1 = 10;
    DVR[3].SET.IN1 = 12;

    DVR[0].SET.IN2 = 4;
    DVR[1].SET.IN2 = 6;
    DVR[2].SET.IN2 = 9;
    DVR[3].SET.IN2 = 11;

    DVR[0].SET.slice = pwm_gpio_to_slice_num(2);
    DVR[1].SET.slice = pwm_gpio_to_slice_num(6);
    DVR[2].SET.slice = pwm_gpio_to_slice_num(8);
    DVR[3].SET.slice = pwm_gpio_to_slice_num(12);

    DVR[0].SET.PWM_CHAN = 0;
    DVR[1].SET.PWM_CHAN = 1;
    DVR[2].SET.PWM_CHAN = 0;
    DVR[3].SET.PWM_CHAN = 1;

    EN_MOT = 14;
    SERVO_PWM = 15;
    slice_ser = pwm_gpio_to_slice_num(14);

    DVR[0].pwm = 0;
    DVR[1].pwm = 0;
    DVR[2].pwm = 0;
    DVR[3].pwm = 0;

    DVR[0].dir = 0;
    DVR[1].dir = 0;
    DVR[2].dir = 0;
    DVR[3].dir = 0;
}

int serv_getang(int ang) {
    int duty = ((ang / 18) * 125) + 1250;
    return duty;
}

void mot_setup() {
    gpio_set_function(15, GPIO_FUNC_PWM);

    for(int i=0;i<4;i++){
        gpio_set_function(DVR[i].SET.PWM, GPIO_FUNC_PWM);

        gpio_init(DVR[i].SET.IN1);
        gpio_set_dir(DVR[i].SET.IN1, GPIO_OUT);

        gpio_init(DVR[i].SET.IN2);
        gpio_set_dir(DVR[i].SET.IN2, GPIO_OUT);
    }

    pwm_set_clkdiv(slice_ser, 100.0);
    pwm_set_wrap(slice_ser, 25000);
    pwm_set_chan_level(slice_ser, PWM_CHAN_B, SERVO_PWM);
    pwm_set_enabled(slice_ser, true);

    for(int i=0;i<4;i++){
        pwm_set_clkdiv(DVR[i].SET.slice, 100.0);
        pwm_set_wrap(DVR[i].SET.slice, 25000);
        pwm_set_chan_level(DVR[i].SET.slice, DVR[i].SET.PWM_CHAN, DVR[i].pwm);
        pwm_set_enabled(DVR[i].SET.slice, true);
    }

}
void external_interrupt(uint gpio, uint32_t events) {
    if(gpio==22);
    if(gpio==21);
}
void extint_setup() {
    gpio_set_irq_enabled_with_callback(21, GPIO_IRQ_EDGE_RISE | GPIO_IRQ_EDGE_FALL, true, &external_interrupt);
    gpio_set_irq_enabled(22, GPIO_IRQ_EDGE_RISE | GPIO_IRQ_EDGE_FALL, true);
}

int main() {

    stdio_init_all();
    var_setup();
    mot_setup();
    extint_setup();

    SERVO_PWM = serv_getang(0);
    pwm_set_chan_level(slice_ser, PWM_CHAN_B, SERVO_PWM);

    while(1){

    }
}
