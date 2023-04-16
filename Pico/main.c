#include <stdio.h>
#include <math.h>
#include <time.h>

#include "pico/stdlib.h"
#include "hardware/pwm.h"
#include "hardware/gpio.h"
#include "hardware/uart.h"
#include "hardware/irq.h"
#include "hardware/clocks.h" //PER SETTARE FREQUENZA CLOCK

#include "pico/multicore.h"
#include "pico/util/queue.h"

#define PLL_SYS_KHZ (125 * 1000)

#define DATA_BITS 8
#define STOP_BITS 1
#define PARITY    UART_PARITY_NONE

#define n_mot 4

#define kp 7000.0
#define ki 200.0
#define kd 400.0
#define diametro 69.0

#define Plim 25000.0
#define Ilim 2000.0 //100.0
#define Dlim 5000.0 //5000.0

typedef struct {
    volatile uint IN1;
    volatile uint IN2;
    volatile uint PWM;
    volatile uint PWM_CHAN;
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
	volatile uint mot;
	volatile double P;
	volatile double I[n_mot];
	volatile double D;
	volatile double correction;
    volatile double old_error[n_mot];
    volatile uint pwm[n_mot];
} def_PID;

typedef struct {
	double trav[4];
	double temp;
} def_dis;

def_driver DVR[n_mot];
def_readspeed RSP[n_mot];
def_PID PID;
def_dis DIS;

queue_t speed_q[n_mot];
queue_t dir_q[n_mot];
queue_t reset_q;
queue_t dist_q;
queue_t pid_q;

volatile int EN_MOT;
volatile int SERVO_PIN_PWM;
volatile uint SERVO_PWM = 1250;
volatile uint slice_ser;

volatile uint RX;
volatile uint TX;

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

void var_setup() {
    DVR[0].PWM = 2;
    DVR[1].PWM = 7;
    DVR[2].PWM = 8;
    DVR[3].PWM = 13;

    DVR[0].IN1 = 3;
    DVR[1].IN1 = 5;
    DVR[2].IN1 = 10;
    DVR[3].IN1 = 11;

    DVR[0].IN2 = 4;
    DVR[1].IN2 = 6;
    DVR[2].IN2 = 9;
    DVR[3].IN2 = 12;

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

    PID.I[0] = 0;
    PID.I[1] = 0;
    PID.I[2] = 0;
    PID.I[3] = 0;

    RSP[0].curr = 4000000000;
    RSP[1].curr = 4000000000;
    RSP[2].curr = 4000000000;
    RSP[3].curr = 4000000000;

    RSP[0].old = 0;
    RSP[1].old = 0;
    RSP[2].old = 0;
    RSP[3].old = 0;

    RSP[0].impulsi = 0;
    RSP[1].impulsi = 0;
    RSP[2].impulsi = 0;
    RSP[3].impulsi = 0;

    DVR[0].corr = -1;
    DVR[1].corr = -1;
    DVR[2].corr = -1;
    DVR[3].corr = -1;

    TX = 0;
    RX = 1;
}

void mot_setup() {
    //GPIO + PWM
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
    pwm_set_wrap(slice_ser, 24999);
    pwm_set_chan_level(slice_ser, PWM_CHAN_B, SERVO_PWM);
    pwm_set_enabled(slice_ser, true);

    for(int i=0;i<4;i++){
        pwm_set_clkdiv(DVR[i].slice, 100.0);
        pwm_set_wrap(DVR[i].slice, 24999);
        pwm_set_chan_level(DVR[i].slice, DVR[i].PWM_CHAN, 10);
        pwm_set_enabled(DVR[i].slice, true);
    }

    //INTERRUPT
    gpio_set_input_enabled(RSP[0].ENC.IN1, true);
    gpio_set_input_enabled(RSP[1].ENC.IN1, true);
    
    gpio_set_irq_enabled_with_callback(RSP[0].ENC.IN1, GPIO_IRQ_EDGE_RISE, true, &enc_interrupt);
    gpio_set_irq_enabled(RSP[1].ENC.IN1, GPIO_IRQ_EDGE_RISE, true);
    gpio_set_irq_enabled(RSP[2].ENC.IN1, GPIO_IRQ_EDGE_RISE, true);
    gpio_set_irq_enabled(RSP[3].ENC.IN1, GPIO_IRQ_EDGE_RISE, true);
}

void uart_setup() {
    uart_init(uart0, 500000);
    gpio_set_function(TX, GPIO_FUNC_UART);
    gpio_set_function(RX, GPIO_FUNC_UART);
    uart_set_format(uart0, DATA_BITS, STOP_BITS, PARITY);

    uart_set_hw_flow(uart0, false, false);
    uart_set_fifo_enabled(uart0, false);
}

uint serv_getduty(int ang) {
    int duty = ((ang / 18.0) * 125.0) + 1875;
    return duty;
}

void driver_set(int mot, int8_t dir, int pwm) {
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

uint8_t pidavv;
bool pid(struct repeating_timer *t) {
    queue_add_blocking(&pid_q, &pidavv);
    return true;
}

void main_1() {

    uint8_t buf, byte[8];

    while(1){
        buf = 0;
        uart_read_blocking(uart0, &buf, 1);
        for(int i=0;i<8;i++){
            byte[i] = buf % 2;
            buf = buf / 2;
        }
        
        if(byte[7] == 0){
            if(byte[6] == 0){
                if(byte[5] != 0){
                    double distanza;
                    queue_try_remove(&dist_q, &distanza);
                    uint8_t temp;
                    uint16_t data;
                    data = (int)(distanza*10.0);

                    for (int k=0; k<2; k++){
                        temp = data % 100;
                        data = data / 100;
                        uart_putc_raw(uart0, temp);
                    }
                }
            }else{
                double marti = 0.0;
                queue_remove_blocking(&dist_q, &marti);
                marti = 0.0;
                int8_t resett = 1;
                queue_add_blocking(&reset_q, &resett);
                queue_add_blocking(&dist_q, &marti);
            }
        }else{ //(BIT 7 == 1)

            double velocita = (byte[5] * 16 + byte[4] * 8 + byte[3] * 4 + byte[2] * 2 + byte[1]) / 20.0;
            int8_t direzione = 1;

            if (byte[0] == 1) {
                direzione = 1;
            } else if(velocita <= 0.1){
                direzione = 0;
            } else{
                direzione = -1;
            }

            if(byte[6] == 0){ //MOT SX
                queue_add_blocking(&speed_q[0], &velocita);
                queue_add_blocking(&speed_q[1], &velocita);
                queue_add_blocking(&dir_q[0], &direzione);
                queue_add_blocking(&dir_q[1], &direzione);
            }else{ //MOT DX
                queue_add_blocking(&speed_q[2], &velocita);
                queue_add_blocking(&speed_q[3], &velocita);
                queue_add_blocking(&dir_q[2], &direzione);
                queue_add_blocking(&dir_q[3], &direzione);
            }
        }

    }
}

int main() {
    set_sys_clock_khz(PLL_SYS_KHZ, true);
    stdio_init_all();

    multicore_launch_core1(main_1);
    var_setup();
    mot_setup();
    uart_setup();

    SERVO_PWM = serv_getduty(0);
    pwm_set_chan_level(slice_ser, PWM_CHAN_B, SERVO_PWM);

    for(int i=0;i<4;i++){
        queue_init(&speed_q[i], sizeof(double), 1);
        queue_init(&dir_q[i], sizeof(int8_t), 1);
    }
    queue_init(&reset_q, sizeof(int8_t), 1);
    queue_init(&dist_q, sizeof(double), 1);
    
    struct repeating_timer timerpid;
    add_repeating_timer_us(-500, pid, NULL, &timerpid);
    queue_init(&pid_q, sizeof(uint8_t), 1);
    
    double speedtemp;
    double speed[n_mot] = {0};
    double speed_error = 0;
    double wanted_speed[n_mot] = {0};
    int wanted_dir[n_mot] = {0};
    uint8_t start;

    for(int i=0;i<4;i++){
        wanted_speed[PID.mot] = 0.0;
        speed[PID.mot] = 0.0;
        DIS.trav[i] = 0.0;
        RSP[i].curr = 4000000000; 
        RSP[i].impulsi = 0;
    }

    while(1) {

        queue_remove_blocking(&pid_q, &start);
        
        PID.mot ++;
        if (PID.mot >= 4) {
            PID.mot = 0;
        }

        queue_try_remove(&speed_q[PID.mot], &wanted_speed[PID.mot]);
        queue_try_remove(&dir_q[PID.mot], &wanted_dir[PID.mot]);
        
        speedtemp = (((double)1000000.0) / (((double)RSP[PID.mot].curr) * 680.0));
        printf("\n%f", speed[PID.mot]);

        if (speedtemp < 2.0) {
            speed[PID.mot] = speedtemp;
        } else if (speed[PID.mot] < 0.01) {
            speed[PID.mot] = 0.0;
            RSP[PID.mot].curr = 4000000000;
        } else{
            speed[PID.mot] += speed[PID.mot] * -0.01;
        }

        PID.P = 0;
        PID.D = 0;
        PID.correction = 0;
        
        if (wanted_speed[PID.mot]  != 0) {
            speed_error = wanted_speed[PID.mot] - speed[PID.mot];
            
            PID.P = speed_error * kp;
            PID.I[PID.mot] += speed_error * ki;
            PID.D = ((speed_error - PID.old_error[PID.mot]) / 0.002)* kd;
            
            PID.old_error[PID.mot] = speed_error;
            
            PID.P = PID.P > Plim ? Plim : PID.P < -Plim ? -Plim : PID.P;
            PID.I[PID.mot] = PID.I[PID.mot] > Ilim ? Ilim : PID.I[PID.mot] < -Ilim ? -Ilim : PID.I[PID.mot];
            PID.D = PID.D > Dlim ? Dlim : PID.D < -Dlim ? -Dlim : PID.D;
            
            PID.correction = PID.P + PID.I[PID.mot] + PID.D + PID.pwm[PID.mot];

            PID.correction = PID.correction > 25000 ? 25000 : PID.correction < 0 ? 0 : PID.correction;
            PID.pwm[PID.mot] = PID.correction;
        }else{
            PID.pwm[PID.mot] = 0;
        }
        driver_set(PID.mot, wanted_dir[PID.mot], PID.correction);
        
        uint8_t reset = 0;
        queue_try_remove(&reset_q, &reset);

        if (reset == 0) {
            DIS.trav[PID.mot] += speed[PID.mot] * 0.002 * 69 * M_PI;
            DIS.temp = 10000.0;

            for(int i=0;i<4;i++){
                if (DIS.trav[i] < DIS.temp)DIS.temp = DIS.trav[i];
            }
            queue_try_add(&dist_q, &DIS.temp);

        }else{
            for(int i=0;i<4;i++){
                speed[PID.mot] = 0.0;
                DIS.trav[i] = 0.0;
                RSP[i].curr = 4000000000; 
                RSP[i].impulsi = 0;
            }
        }
    }    
}
