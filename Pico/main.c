#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/pwm.h"
#include "hardware/gpio.h"

typedef struct {
	volatile char dir;
    volatile int pwm;
} def_set;

typedef struct {
    volatile uint IN1;
    volatile uint IN2;
    volatile uint PWM;
    volatile int PWM_CHAN;
    volatile uint slice;
    volatile def_set SET;
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

def_driver DVR[4];
def_readspeed RSP[4];

volatile int EN_MOT;
volatile int SERVO_PIN_PWM;
volatile int SERVO_PWM = 1250;
volatile uint slice_ser;

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

    DVR[0].slice = pwm_gpio_to_slice_num(2);
    DVR[1].slice = pwm_gpio_to_slice_num(6);
    DVR[2].slice = pwm_gpio_to_slice_num(8);
    DVR[3].slice = pwm_gpio_to_slice_num(12);

    DVR[0].PWM_CHAN = 0;
    DVR[1].PWM_CHAN = 1;
    DVR[2].PWM_CHAN = 0;
    DVR[3].PWM_CHAN = 1;

    EN_MOT = 14;
    SERVO_PWM = 15;
    slice_ser = pwm_gpio_to_slice_num(14);

    DVR[0].SET.pwm = 0;
    DVR[1].SET.pwm = 0;
    DVR[2].SET.pwm = 0;
    DVR[3].SET.pwm = 0;

    DVR[0].SET.dir = 0;
    DVR[1].SET.dir = 0;
    DVR[2].SET.dir = 0;
    DVR[3].SET.dir = 0;

    RSP[0].ENC.IN1 = 26;
    RSP[1].ENC.IN1 = 28;
    RSP[2].ENC.IN1 = 18;
    RSP[3].ENC.IN1 = 20;
    
    RSP[0].ENC.IN2 = 22;
    RSP[1].ENC.IN2 = 27;
    RSP[2].ENC.IN2 = 19;
    RSP[3].ENC.IN2 = 21;

    RSP[0].curr = timer_hw->timelr;
    RSP[1].curr = timer_hw->timelr;
    RSP[2].curr = timer_hw->timelr;
    RSP[3].curr = timer_hw->timelr;

    RSP[0].old = 0;
    RSP[1].old = 0;
    RSP[2].old = 0;
    RSP[3].old = 0;

}

int serv_getang(int ang) {
    int duty = ((ang / 18) * 125) + 1250;
    return duty;
}

void mot_setup() {
    gpio_set_function(15, GPIO_FUNC_PWM);

    for(int i=0;i<4;i++){
        gpio_set_function(DVR[i].PWM, GPIO_FUNC_PWM);

        gpio_init(DVR[i].IN1);
        gpio_set_dir(DVR[i].IN1, GPIO_OUT);

        gpio_init(DVR[i].IN2);
        gpio_set_dir(DVR[i].IN2, GPIO_OUT);
    }

    pwm_set_clkdiv(slice_ser, 100.0);
    pwm_set_wrap(slice_ser, 25000);
    pwm_set_chan_level(slice_ser, PWM_CHAN_B, SERVO_PWM);
    pwm_set_enabled(slice_ser, true);

    for(int i=0;i<4;i++){
        pwm_set_clkdiv(DVR[i].slice, 100.0);
        pwm_set_wrap(DVR[i].slice, 25000);
        pwm_set_chan_level(DVR[i].slice, DVR[i].PWM_CHAN, DVR[i].SET.pwm);
        pwm_set_enabled(DVR[i].slice, true);
    }

}

void int_mot1(uint gpio, uint32_t events){
	RSP[0].impulsi ++;
}
void int_mot2(uint gpio, uint32_t events){
	RSP[1].impulsi ++;
}
void int_mot3(uint gpio, uint32_t events){
	RSP[2].impulsi ++;
}
void int_mot4(uint gpio, uint32_t events){
	RSP[3].impulsi ++;
}

void extint_setup() {
	gpio_set_input_enabled(26, true);
    gpio_set_input_enabled(27, true);
    gpio_set_input_enabled(28, true);
    gpio_set_irq_enabled_with_callback(RSP[0].ENC.IN1, GPIO_IRQ_EDGE_RISE, true, &int_mot1);
    //gpio_set_irq_enabled_with_callback(RSP[1].ENC.IN1, GPIO_IRQ_EDGE_RISE, true, &int_mot2);
    //gpio_set_irq_enabled_with_callback(RSP[2].ENC.IN1, GPIO_IRQ_EDGE_RISE, true, &int_mot3);
    //gpio_set_irq_enabled_with_callback(RSP[3].ENC.IN1, GPIO_IRQ_EDGE_RISE, true, &int_mot4);
}

int main() {

    stdio_init_all();
    var_setup();
    mot_setup();
    extint_setup();

    SERVO_PWM = serv_getang(0);
    pwm_set_chan_level(slice_ser, PWM_CHAN_B, SERVO_PWM);

    while(1){
        for(int i=0;i<4;i++){
            printf("MOT %d : %d \n", i, RSP[i].impulsi);
            sleep_ms(500);
        }
    }
}
