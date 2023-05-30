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

#define kp 14000.0
#define ki 400.0
#define kd 800.0
#define diametro 69.0

#define Plim 50000.0
#define Ilim 4000.0
#define Dlim 10000.0

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

queue_t kitd_q;
queue_t kits_q;

volatile int EN_MOT;
volatile int SERVO_PIN_PWM;
volatile uint SERVO_PWM;
volatile uint slice_ser;
volatile uint serv_0;

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
	
	serv_0 = 1875;

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
    pwm_set_wrap(slice_ser, 25000);
    pwm_set_chan_level(slice_ser, PWM_CHAN_B, serv_0);
    pwm_set_enabled(slice_ser, true);

    for(int i=0;i<4;i++){
        pwm_set_clkdiv(DVR[i].slice, 50.0);
        pwm_set_wrap(DVR[i].slice, 50000);
        pwm_set_chan_level(DVR[i].slice, DVR[i].PWM_CHAN, 1);
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
    uart_init(uart0, 1000000);
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
    }else if (dir == 0){ //FRENA
        pwm_set_chan_level(DVR[mot].slice, DVR[mot].PWM_CHAN, 0);
        gpio_put(DVR[mot].IN1, 1);
        gpio_put(DVR[mot].IN2, 1);
    }else if ((dir == 2) || (dir == -2)){ //OFF
        gpio_put(DVR[mot].IN1, 0);
        gpio_put(DVR[mot].IN2, 0);
    }
    pwm_set_chan_level(DVR[mot].slice, DVR[mot].PWM_CHAN, pwm);
}

uint8_t kitd = 0;
uint8_t gkitd = 0;
uint8_t kits = 0;
uint8_t gkits = 0;
bool kit(struct repeating_timer *t) {

    gkitd = 0;
    gkits = 0;
    queue_try_remove(&kitd_q, &gkitd);
    kitd += gkitd;
    queue_try_remove(&kits_q, &gkits);
    kits += gkits;

    if(kitd > 0){
        if(SERVO_PWM == serv_0){
            SERVO_PWM = SERVO_PWM = serv_getduty(180);
            kitd--;
        }else{
            SERVO_PWM = serv_0;
        }
    }else if(kits > 0){
        if(SERVO_PWM == serv_0){
            SERVO_PWM = SERVO_PWM = serv_getduty(-180);
            kits--;
        }else{
            SERVO_PWM = serv_0;
        }
    }else{
        SERVO_PWM = serv_0;
    }

    pwm_set_chan_level(slice_ser, PWM_CHAN_B, SERVO_PWM);

    return true;
}

bool pid(struct repeating_timer *t) {
    uint8_t pidavv;
    queue_add_blocking(&pid_q, &pidavv);
    return true;
}

void main_1() {

    uint8_t buf, vel;
    uint8_t byte[8];
    uint8_t check = false;
    uint serialerror = 0;

    while(1){
        
        check = uart_is_readable_within_us(uart0, 2000);

        if(check == false){

            serialerror += 1;
            if(serialerror == 250){
                int8_t resett = 1;
                for(int i=0;i<4;i++){
                    driver_set(i, 0, 0);
                }
                queue_try_add(&reset_q, &resett);
            }

        }else{ //SERIALE LEGGIBILE

            buf = 0;
            uart_read_blocking(uart0, &buf, 1);
            for(int i=0;i<8;i++){
                byte[i] = (buf >> i) & 1;
            }
            
            if(byte[7] == 0){

                if((byte[6] == 0) && (byte[5] == 1)){ //SET MOTORI

                    check = uart_is_readable_within_us(uart0, 2000);

                    if(check == false){

                        serialerror += 1;

                    }else{

                        uart_read_blocking(uart0, &buf, 1);
                        vel = buf;
                        buf = (buf >> 7) & 1;

                        if(buf == 1){
                            
                            double velocita = (vel & 127) / 50.0;
                            int8_t direzione;
                            int8_t sx;

                            if((byte[1] == 1) && (byte[0] == 1)){ //FRENA
                                direzione = 0;
                            }else if((byte[1] == 0) && (byte[0] == 1)){
                                direzione = 1;
                            }else if((byte[1] == 1) && (byte[0] == 0)){
                                direzione = -1;
                            }else{ //OFF
                                direzione = 2;
                            }

                            if(byte[2] == 0){
                                sx = 0;
                            }else{
                                sx = 2;
                            }

                            double sus;
                            int8_t sus1;

                            queue_try_remove(&speed_q[sx], &sus);
                            queue_try_remove(&speed_q[sx+1], &sus);
                            queue_try_remove(&dir_q[sx], &sus1);
                            queue_try_remove(&dir_q[sx+1], &sus1);

                            queue_try_add(&speed_q[sx], &velocita);
                            queue_try_add(&speed_q[sx+1], &velocita);
                            queue_try_add(&dir_q[sx], &direzione);
                            queue_try_add(&dir_q[sx+1], &direzione);

                        }
                
                    }
                
                }else if((byte[6] == 1) && (byte[5] == 0)){ //RICHIESTE

                    if((byte[4] == 0) && (byte[3] == 0)){ //RESET DISTANZA

                        double marti = 0.0;
                        queue_try_remove(&dist_q, &marti);
                        marti = 0.0;
                        int8_t resett = 1;
                        queue_try_add(&reset_q, &resett);
                        queue_try_add(&dist_q, &marti);

                    }else if((byte[4] == 0) && (byte[3] == 1)){ //MANDA DISTANZA

                        double distanza;
                        queue_try_remove(&dist_q, &distanza);
                        uint8_t temp;
                        uint16_t data;
                        data = (int)(distanza*10.0);

                        temp = data >> 8;
                        uart_putc_raw(uart0, temp);
                        temp = data;
                        uart_putc_raw(uart0, temp);

                    }else if((byte[4] == 1) && (byte[3] == 0)){ //KIT

                        uint8_t kit;

                        kit = byte[1] * 2 + byte[0];

                        buf = 0;
                        if(byte[2] == 1){
                            queue_try_remove(&kitd_q, &buf);
                            kit += buf;
                            queue_try_add(&kitd_q, &kit);
                        }else{
                            queue_try_remove(&kits_q, &buf);
                            kit += buf;
                            queue_try_add(&kits_q, &kit);
                        }

                    }

                }

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

    gpio_init(PICO_DEFAULT_LED_PIN);
    gpio_set_dir(PICO_DEFAULT_LED_PIN, GPIO_OUT);

    gpio_put(PICO_DEFAULT_LED_PIN, 0);

    for(int i=0;i<4;i++){
        queue_init(&speed_q[i], sizeof(double), 1);
        queue_init(&dir_q[i], sizeof(int8_t), 1);
    }
    queue_init(&reset_q, sizeof(int8_t), 1);
    queue_init(&dist_q, sizeof(double), 1);

    queue_init(&kitd_q, sizeof(int8_t), 1);
    queue_init(&kits_q, sizeof(int8_t), 1);
    
    struct repeating_timer timerpid;
    add_repeating_timer_us(-500, pid, NULL, &timerpid);
    queue_init(&pid_q, sizeof(uint8_t), 1);
    
    struct repeating_timer timerkit;
    add_repeating_timer_ms(500, kit, NULL, &timerkit);    

    double speedtemp;
    double speed[n_mot] = {0};
    double speed_error = 0;
    double wanted_speed[n_mot] = {0};
    int wanted_dir[n_mot] = {0};
    uint8_t start;

    for(int i=0;i<4;i++){
        wanted_speed[i] = 0.0;
        speed[i] = 0.0;
        DIS.trav[i] = 0.0;
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

        if (speedtemp < 2.0) {
            speed[PID.mot] = speedtemp;
        } else if (speed[PID.mot] < 0.1) {
            speed[PID.mot] = 0.0;
            RSP[PID.mot].curr = 4000000000;
        } else{
            speed[PID.mot] += speed[PID.mot] * -0.05;
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

            PID.correction = PID.correction > 50000 ? 50000 : PID.correction < 0 ? 0 : PID.correction;
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

            if(DIS.temp>290){
                gpio_put(PICO_DEFAULT_LED_PIN, 1);
            } else{
                gpio_put(PICO_DEFAULT_LED_PIN, 0);
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
