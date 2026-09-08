/* 霍尔状态到换相步骤的映射表 (120° 布局，霍尔状态 CBA，值范围0-7) */
/*static const uint8_t hall_to_step_map[8] = {
    0xFF,   // 0: 无效 
    5,      // 1: 步骤1 
    3,      // 2: 步骤3 
    4,      // 3: 步骤2 
    1,      // 4: 步骤5 
    0,      // 5: 步骤0 
    2,      // 6: 步骤4 
    0xFF    // 7: 无效 
};
*/

/**
  * @file    main.c
  * @brief   CH32V230C8T6 带霍尔传感器 BLDC 六步换相控制程序（纯 GPIO 驱动，无 PWM）
  * @note    硬件连接：
  *          - 三相下桥臂：PA0 (U_LO), PA1 (V_LO), PA4 (W_LO)
  *          - 三相上桥臂：PA8 (U_HI), PA9 (V_HI), PA10 (W_HI)
  *          - 霍尔传感器：PB3 (HALL_A), PB4 (HALL_B), PB5 (HALL_C) 配置为 EXTI 中断
  *          - 启动/停止控制：PB0 (按钮)
  *
  *          ?? 电机将以全电压驱动，请确保电源限流或电机功率较小。
  */

#include "ch32v20x.h"
#include "debug.h"
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* 引脚宏定义 -----------------------------------------------------------------*/
/* 下桥臂输出引脚 (GPIO 直接控制) */
#define LO_U_PORT          GPIOA
#define LO_U_PIN           GPIO_Pin_0
#define LO_V_PORT          GPIOA
#define LO_V_PIN           GPIO_Pin_1
#define LO_W_PORT          GPIOA
#define LO_W_PIN           GPIO_Pin_4      /* 修改为 PA4 */

/* 上桥臂输出引脚 (GPIO 直接控制) */
#define HI_U_PORT          GPIOA
#define HI_U_PIN           GPIO_Pin_8
#define HI_V_PORT          GPIOA
#define HI_V_PIN           GPIO_Pin_9
#define HI_W_PORT          GPIOA
#define HI_W_PIN           GPIO_Pin_10

/* 霍尔传感器输入引脚 - 重新分配 */
#define HALL_A_PORT        GPIOB
#define HALL_A_PIN         GPIO_Pin_3      /* HALL_A -> PB3 */
#define HALL_B_PORT        GPIOB
#define HALL_B_PIN         GPIO_Pin_4      /* HALL_B -> PB4 */
#define HALL_C_PORT        GPIOB
#define HALL_C_PIN         GPIO_Pin_5      /* HALL_C -> PB5 */

/* 电机电源控制 (低电平关断) */
#define MOTOR_PWR_CTRL_PORT  GPIOA
#define MOTOR_PWR_CTRL_PIN   GPIO_Pin_5
#define MotorPower_Off()     GPIO_ResetBits(MOTOR_PWR_CTRL_PORT, MOTOR_PWR_CTRL_PIN)
#define MotorPower_On()      GPIO_SetBits(MOTOR_PWR_CTRL_PORT, MOTOR_PWR_CTRL_PIN)

/* 电机电源就绪信号 (低电平表示就绪) */
#define MOTOR_PWR_RDY_PORT   GPIOA
#define MOTOR_PWR_RDY_PIN    GPIO_Pin_6
#define IsMotorPowerReady()  (GPIO_ReadInputDataBit(MOTOR_PWR_RDY_PORT, MOTOR_PWR_RDY_PIN) == RESET)

/* 到位信号 (高电平表示到位) */
#define IN_POSITION_PORT     GPIOA
#define IN_POSITION_PIN      GPIO_Pin_7
#define IsInPosition()       (GPIO_ReadInputDataBit(IN_POSITION_PORT, IN_POSITION_PIN) == RESET)

/* 串口2配置 */
#define UART_BAUD_RATE       9600
#define USART1_RX_SIZE    512

/* 启动/停止按钮引脚 */
#define BTN_START_PORT     GPIOB
#define BTN_START_PIN      GPIO_Pin_0

//lora电源开关
#define LORA_OFF()      GPIO_SetBits(GPIOB, GPIO_Pin_8)
#define LORA_ON()      GPIO_ResetBits(GPIOB, GPIO_Pin_8)

/* 全局变量 -------------------------------------------------------------------*/
volatile bool motor_running = false;      /* 电机运行标志 */
volatile uint8_t hall_state = 0;          /* 当前霍尔状态 (CBA) */
volatile uint8_t commutation_step = 10;    /* 当前换相步骤 (0-5) */
volatile int stp_count = 0;
volatile int32_t hall_cycle_count = 0;    /* 霍尔换相次数计数 (每60°一次) */
volatile int32_t hall_cycle_count2 = 0;    /* 霍尔换相次数计数 (每60°一次) */
volatile int32_t target_hall_cycles = 0;  /* 目标霍尔换相次数 (一圈=6次) */
volatile bool motor_stop_request = false; /* 停止请求 */
volatile bool motor_power_on = false;     /* 电机电源状态 */
u8 hall_states[500];
u8 pin_states[500];
u8 RxBuffer1[USART1_RX_SIZE] = {0};
volatile u16 rx1_cnt = 0;
volatile u16 senscount = 0;

/* 死区延时微秒数 (防止上下桥臂直通) */
#define DEAD_TIME_US       5

/* 函数声明 */
static void all_outputs_off(void);
static void set_outputs_for_step(uint8_t step);
static uint8_t read_hall_state(void);
static void hall_update(void);
static void motor_power_init(void);
static void motor_power_off(void);
static void motor_power_on_and_wait(void);



/* 关闭所有 MOSFET 输出 (所有上桥臂和下桥臂均设置为低电平) */
static void all_outputs_off(void) {
    /* 上桥臂全部设为低电平 (关闭) */
    GPIO_ResetBits(HI_U_PORT, HI_U_PIN);
    GPIO_ResetBits(HI_V_PORT, HI_V_PIN);
    GPIO_ResetBits(HI_W_PORT, HI_W_PIN);
    /* 下桥臂全部设为低电平 (关闭) */
    GPIO_ResetBits(LO_U_PORT, LO_U_PIN);
    GPIO_ResetBits(LO_V_PORT, LO_V_PIN);
    GPIO_ResetBits(LO_W_PORT, LO_W_PIN);
}

/* 刹车 */
static void outputs_break(void) {
    /* 上桥臂全部设为低电平 (关闭) */
    GPIO_ResetBits(HI_U_PORT, HI_U_PIN);
    GPIO_ResetBits(HI_V_PORT, HI_V_PIN);
    GPIO_ResetBits(HI_W_PORT, HI_W_PIN);
    /* 下桥臂全部设为高电平 (打开) */
    GPIO_SetBits(LO_U_PORT, LO_U_PIN);
    GPIO_SetBits(LO_V_PORT, LO_V_PIN);
    GPIO_SetBits(LO_W_PORT, LO_W_PIN);
}

/* 根据换相步骤设置各 GPIO 输出 (假设高电平导通，低电平关断) */
static void set_outputs_for_step(uint8_t step) {
    /* 先关闭所有输出 */
    all_outputs_off();
    if(step > 5)
    {
        return;;
    }
    /* 插入死区延时，防止直通 */
    //delay_us(DEAD_TIME_US);
    
    /* 换相表: {上桥臂引脚, 下桥臂引脚} (以步骤0-5) */
    typedef struct {
        uint16_t hi_pin;
        GPIO_TypeDef* hi_port;
        uint16_t lo_pin;
        GPIO_TypeDef* lo_port;
    } PhasePins_t;
    
    const PhasePins_t phase_table[6] = {
        /* 步骤0: V_HI + W_LO */
        {HI_V_PIN, HI_V_PORT, LO_W_PIN, LO_W_PORT},
        /* 步骤1: U_HI + W_LO */
        {HI_U_PIN, HI_U_PORT, LO_W_PIN, LO_W_PORT},
        /* 步骤2: U_HI + V_LO */
        {HI_U_PIN, HI_U_PORT, LO_V_PIN, LO_V_PORT},
        /* 步骤3: W_HI + V_LO */
        {HI_W_PIN, HI_W_PORT, LO_V_PIN, LO_V_PORT},
        /* 步骤4: W_HI + U_LO */
        {HI_W_PIN, HI_W_PORT, LO_U_PIN, LO_U_PORT},
        /* 步骤5: V_HI + U_LO */
        {HI_V_PIN, HI_V_PORT, LO_U_PIN, LO_U_PORT},
    };
    
    const PhasePins_t* p = &phase_table[step];
    /* 打开对应的上桥臂和下桥臂 */
    GPIO_SetBits(p->hi_port, p->hi_pin);
    GPIO_SetBits(p->lo_port, p->lo_pin);
}

/* 霍尔状态到换相步骤的映射表 (120° 布局，霍尔状态 CBA，值范围0-7) */
static const uint8_t hall_to_step_map[8] = {
    0xFF,   /* 0: 无效 */
    1,      /* 1: 步骤1 */
    3,      /* 2: 步骤3 */
    2,      /* 3: 步骤2 */
    5,      /* 4: 步骤5 */
    0,      /* 5: 步骤0 */
    4,      /* 6: 步骤4 */
    0xFF    /* 7: 无效 */
};

/* 读取霍尔状态 (低3位: bit0=A, bit1=B, bit2=C) */
static uint8_t read_hall_state(void) {
    uint8_t state = 0;
    if (GPIO_ReadInputDataBit(HALL_A_PORT, HALL_A_PIN)) state |= (1 << 0);
    if (GPIO_ReadInputDataBit(HALL_B_PORT, HALL_B_PIN)) state |= (1 << 1);
    if (GPIO_ReadInputDataBit(HALL_C_PORT, HALL_C_PIN)) state |= (1 << 2);
    return state;
}

/* 霍尔信号变化时更新换相 (在中断中调用) */
static void hall_update(void) {
    uint8_t new_hall = read_hall_state();
    hall_states[hall_cycle_count2] = new_hall;
    pin_states[hall_cycle_count2] = IsInPosition();
    hall_cycle_count2++;
    if(hall_cycle_count2 == 500)
    {
        hall_cycle_count2 = 0;
    }
    //if (new_hall == hall_state) return;
    
    hall_state = new_hall;
    if (!motor_running) 
    {
        /* 先关闭所有输出 */
        all_outputs_off();
        return;
    }
    
    if (hall_state < 8 && hall_to_step_map[hall_state] != 0xFF) {
        //uint8_t new_step = hall_to_step_map[hall_state];
        set_outputs_for_step(hall_to_step_map[hall_state]);

        //if (new_step != commutation_step) {
        //    commutation_step = new_step;
        //    stp_count++;
        //    commutation_step = new_step;
        //    set_outputs_for_step(commutation_step);
        //    hall_cycle_count++;
        // if (1) {
        //    if(stp_count > 0)
        //    {
        //        stp_count--;
        //        commutation_step = new_step;
        //        set_outputs_for_step(commutation_step);
        //        hall_cycle_count++;
        //    }
        //    else {
        //        all_outputs_off();
        //        //outputs_break();
        //        stp_count = 0;
        //        motor_running = false;
        //    }
            
        //}
    }
    /* 无效霍尔状态: 不换相，维持原输出 */
}

/* 硬件初始化 -----------------------------------------------------------------*/
static void RCC_Configuration(void) {
    SystemCoreClockUpdate();
    /* 使能 GPIOA, GPIOB, AFIO 时钟 */
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA | RCC_APB2Periph_GPIOB | RCC_APB2Periph_AFIO, ENABLE);
}

static void GPIO_Configuration(void) {
    GPIO_InitTypeDef GPIO_InitStructure = {0};
    
    /* 上桥臂输出引脚: 推挽输出，50MHz */
    GPIO_InitStructure.GPIO_Pin   = HI_U_PIN | HI_V_PIN | HI_W_PIN;
    GPIO_InitStructure.GPIO_Mode  = GPIO_Mode_Out_PP;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_Init(GPIOA, &GPIO_InitStructure);
    
    /* 下桥臂输出引脚: 推挽输出 (PA0, PA1, PA4) */
    GPIO_InitStructure.GPIO_Pin   = LO_U_PIN | LO_V_PIN | LO_W_PIN;
    GPIO_Init(GPIOA, &GPIO_InitStructure);
    
    /* 霍尔传感器输入引脚: 浮空输入 (PB3, PB4, PB5) */
    GPIO_InitStructure.GPIO_Pin   = HALL_A_PIN | HALL_B_PIN | HALL_C_PIN;
    GPIO_InitStructure.GPIO_Mode  = GPIO_Mode_IN_FLOATING;
    GPIO_Init(HALL_A_PORT, &GPIO_InitStructure);
    
    /* 按钮引脚: 上拉输入 (PB0) */
    GPIO_InitStructure.GPIO_Pin   = BTN_START_PIN;
    GPIO_InitStructure.GPIO_Mode  = GPIO_Mode_IPU;
    GPIO_Init(BTN_START_PORT, &GPIO_InitStructure);
    
    /* 初始将所有输出设为低电平 (关闭) */
    all_outputs_off();
}

/* 配置霍尔引脚为 EXTI 中断 (双边沿触发) */
static void HALL_EXTI_Configuration(void) {
    EXTI_InitTypeDef EXTI_InitStructure = {0};
    NVIC_InitTypeDef NVIC_InitStructure = {0};
    
    /* 连接 EXTI 线到 GPIO 引脚 */
    GPIO_EXTILineConfig(GPIO_PortSourceGPIOB, GPIO_PinSource3);  /* PB3 -> EXTI3 */
    GPIO_EXTILineConfig(GPIO_PortSourceGPIOB, GPIO_PinSource4);  /* PB4 -> EXTI4 */
    GPIO_EXTILineConfig(GPIO_PortSourceGPIOB, GPIO_PinSource5);  /* PB5 -> EXTI5 */
    
    /* 配置 EXTI 线 (注意 EXTI 线编号与引脚号对应) */
    EXTI_InitStructure.EXTI_Mode    = EXTI_Mode_Interrupt;
    EXTI_InitStructure.EXTI_Trigger = EXTI_Trigger_Rising_Falling;
    EXTI_InitStructure.EXTI_LineCmd = DISABLE; //没开电源要关闭中断
    
    /* 配置 EXTI Line3 (PB3) */
    EXTI_InitStructure.EXTI_Line    = EXTI_Line3;
    EXTI_Init(&EXTI_InitStructure);
    
    /* 配置 EXTI Line4 (PB4) */
    EXTI_InitStructure.EXTI_Line    = EXTI_Line4;
    EXTI_Init(&EXTI_InitStructure);
    
    /* 配置 EXTI Line5 (PB5) */
    EXTI_InitStructure.EXTI_Line    = EXTI_Line5;
    EXTI_Init(&EXTI_InitStructure);
    
    /* 配置 NVIC 中断优先级 */
    NVIC_InitStructure.NVIC_IRQChannelPreemptionPriority = 1;
    NVIC_InitStructure.NVIC_IRQChannelSubPriority = 0;
    NVIC_InitStructure.NVIC_IRQChannelCmd = ENABLE;
    
    /* EXTI3 中断 (对应 PB3) */
    NVIC_InitStructure.NVIC_IRQChannel = EXTI3_IRQn;
    NVIC_Init(&NVIC_InitStructure);
    
    /* EXTI4 中断 (对应 PB4) */
    NVIC_InitStructure.NVIC_IRQChannel = EXTI4_IRQn;
    NVIC_Init(&NVIC_InitStructure);
    
    /* EXTI9_5 中断 (对应 PB5) */
    NVIC_InitStructure.NVIC_IRQChannel = EXTI9_5_IRQn;
    NVIC_Init(&NVIC_InitStructure);
}

static void HALL_EXTI_Off(void) {
    EXTI_InitTypeDef EXTI_InitStructure = {0};
    
    
    /* 配置 EXTI 线 (注意 EXTI 线编号与引脚号对应) */
    EXTI_InitStructure.EXTI_LineCmd = DISABLE; //关中断清中断
    EXTI_InitStructure.EXTI_Line    = EXTI_Line3 | EXTI_Line4 | EXTI_Line5;
    EXTI_Init(&EXTI_InitStructure);

    EXTI_ClearITPendingBit(EXTI_Line3);
    EXTI_ClearITPendingBit(EXTI_Line4);
    EXTI_ClearITPendingBit(EXTI_Line5);
    
}

static void HALL_EXTI_On(void) {
    EXTI_InitTypeDef EXTI_InitStructure = {0};
    
    EXTI_ClearITPendingBit(EXTI_Line3);
    EXTI_ClearITPendingBit(EXTI_Line4);
    EXTI_ClearITPendingBit(EXTI_Line5);

    /* 配置 EXTI 线 (注意 EXTI 线编号与引脚号对应) */
    EXTI_InitStructure.EXTI_Mode    = EXTI_Mode_Interrupt;
    EXTI_InitStructure.EXTI_Trigger = EXTI_Trigger_Rising_Falling;
    EXTI_InitStructure.EXTI_LineCmd = ENABLE; //
    EXTI_InitStructure.EXTI_Line    = EXTI_Line3 | EXTI_Line4 | EXTI_Line5;
    EXTI_Init(&EXTI_InitStructure);

    
    
}

/* 中断服务函数 -----------------------------------------------------------------*/

void EXTI3_IRQHandler(void) __attribute__((interrupt("WCH-Interrupt-fast")));
void EXTI3_IRQHandler(void) {
    if (EXTI_GetITStatus(EXTI_Line3) != RESET) {
        hall_update();
        EXTI_ClearITPendingBit(EXTI_Line3);
    }
}

void EXTI4_IRQHandler(void) __attribute__((interrupt("WCH-Interrupt-fast")));
void EXTI4_IRQHandler(void) {
    if (EXTI_GetITStatus(EXTI_Line4) != RESET) {
        hall_update();
        EXTI_ClearITPendingBit(EXTI_Line4);
    }
}

void EXTI9_5_IRQHandler(void) __attribute__((interrupt("WCH-Interrupt-fast")));
void EXTI9_5_IRQHandler(void) {
    if (EXTI_GetITStatus(EXTI_Line5) != RESET) {
        hall_update();
        EXTI_ClearITPendingBit(EXTI_Line5);
    }
}

/* 电机电源初始化 */
static void motor_power_init(void) {
    GPIO_InitTypeDef GPIO_InitStructure = {0};
    
    /* 电源控制引脚 */
    GPIO_InitStructure.GPIO_Pin = MOTOR_PWR_CTRL_PIN;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_Out_PP;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_Init(MOTOR_PWR_CTRL_PORT, &GPIO_InitStructure);
    
    /* 电源就绪信号引脚 */
    GPIO_InitStructure.GPIO_Pin = MOTOR_PWR_RDY_PIN;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IN_FLOATING;
    GPIO_Init(MOTOR_PWR_RDY_PORT, &GPIO_InitStructure);
    
    /* 到位信号引脚 */
    GPIO_InitStructure.GPIO_Pin = IN_POSITION_PIN;
    GPIO_Init(MOTOR_PWR_RDY_PORT, &GPIO_InitStructure);
    
    /* 初始状态：关断电机电源 */
    MotorPower_Off();
    motor_power_on = false;
}

/* 关断电机电源 */
static void motor_power_off(void) {
    MotorPower_Off();

    motor_power_on = false;
}

/* 开启电机电源并等待就绪 */
static void motor_power_on_and_wait(void) {
    if (motor_power_on) return;
    
    MotorPower_On();
    
    /* 等待电源就绪，超时1000ms */
    uint32_t timeout = 1000;
    while (!IsMotorPowerReady() && timeout) {
        Delay_Ms(1);
        timeout --;
    }
    //超时电源没打开，关闭电源，并进入死循环
    if(timeout == 0)
    {
        motor_power_off();
        printf("Open moto power ***FAIL***\r\n");
        while(1);
    }
    printf("Open moto power ---SUCCESS---\r\n");    
    
    motor_power_on = true;
}

void start_motor(void)
{
     //打开电机电源，延时等待霍尔等
    HALL_EXTI_Off();
    motor_power_on_and_wait();
    outputs_break(); //下管充电
    Delay_Ms(300);
    HALL_EXTI_On();
    motor_running = true;   /* 转动电机 */
    hall_update();
}

void stop_motor(void)
{
    motor_running = false;   /* 关闭电机 */
    //等待0.5秒
    Delay_Ms(500);
    //关闭电源    
    motor_power_off();

    /* 等待电源关闭，超时1000ms */
    uint32_t timeout = 1000;
    while (IsMotorPowerReady() && timeout) {
        Delay_Ms(1);
        timeout --;
    }
    //超时电源没关闭，关闭电源，并进入死循环
    if(timeout == 0)
    {
        printf("Close moto power ***FAIL***\r\n");
        while(1);
    }
    printf("Close moto power ---SUCCESS---\r\n");

}

void USART3_IRQHandler(void) __attribute__((interrupt("WCH-Interrupt-fast")));
void USART3_IRQHandler(void) {
    if (USART_GetITStatus(USART3, USART_IT_RXNE) != RESET) {
        RxBuffer1[rx1_cnt] = USART_ReceiveData(USART3);  // 读取数据会自动清除RXNE标志
        rx1_cnt++;
        if(rx1_cnt == 512)
        {
            rx1_cnt = 0;
        }
    }
}

void USART3_Init(u32 baudrate) {
    // 1. 开启GPIOB和USART3的时钟（USART3在APB1总线上）
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOB, ENABLE);
    RCC_APB1PeriphClockCmd(RCC_APB1Periph_USART3, ENABLE);

    // 2. 配置PB10(TX)和PB11(RX)为复用功能（默认引脚，无需重映射）
    GPIO_InitTypeDef GPIO_InitStructure;
    
    // PB10 - TX (复用推挽输出)
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_10;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF_PP;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_Init(GPIOB, &GPIO_InitStructure);
    
    // PB11 - RX (浮空输入)
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_11;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IN_FLOATING;
    GPIO_Init(GPIOB, &GPIO_InitStructure);

    // 3. 配置USART3参数：9600 8N1
    USART_InitTypeDef USART_InitStructure;
    USART_InitStructure.USART_BaudRate = baudrate;
    USART_InitStructure.USART_WordLength = USART_WordLength_8b;
    USART_InitStructure.USART_StopBits = USART_StopBits_1;
    USART_InitStructure.USART_Parity = USART_Parity_No;
    USART_InitStructure.USART_HardwareFlowControl = USART_HardwareFlowControl_None;
    USART_InitStructure.USART_Mode = USART_Mode_Tx | USART_Mode_Rx;
    USART_Init(USART3, &USART_InitStructure);

    // 4. 使能接收中断
    USART_ITConfig(USART3, USART_IT_RXNE, ENABLE);

    // 5. 配置NVIC中断
    NVIC_InitTypeDef NVIC_InitStructure;
    NVIC_InitStructure.NVIC_IRQChannel = USART3_IRQn;
    NVIC_InitStructure.NVIC_IRQChannelPreemptionPriority = 1;
    NVIC_InitStructure.NVIC_IRQChannelSubPriority = 0;
    NVIC_InitStructure.NVIC_IRQChannelCmd = ENABLE;
    NVIC_Init(&NVIC_InitStructure);

    // 6. 使能USART3
    USART_Cmd(USART3, ENABLE);
}

void lora_init(void) 
{
    GPIO_InitTypeDef GPIO_InitStructure;

    // PB8 lora电源，低电平为开
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_8;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_Out_PP;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_Init(GPIOB, &GPIO_InitStructure);

    LORA_OFF();
}

/* 主函数 ---------------------------------------------------------------------*/
int main(void) {
    bool last_btn_state = true;
    u16 rx_printf = 0;
    u16 tmp_rx;

    motor_power_on = false;
    motor_running = false;
    
    NVIC_PriorityGroupConfig(NVIC_PriorityGroup_1);
    SystemCoreClockUpdate();
    Delay_Init();
    USART_Printf_Init(115200);
    printf("SystemClk:%d\r\n", SystemCoreClock);
    printf( "ChipID:%08x\r\n", DBGMCU_GetCHIPID() );
    printf("This is printf example\r\n");
    Delay_Ms(500);

    RCC_Configuration();
    GPIO_Configuration();
    HALL_EXTI_Configuration();
    motor_power_init();

    lora_init();
    rx_printf = rx1_cnt;
    USART3_Init(9600);

    //关闭电机电源
    all_outputs_off();
    stop_motor();
    Delay_Ms(2000);

    /*
    printf("1st motor test\r\n");
    start_motor();
    Delay_Ms(2000);
    stop_motor();
    Delay_Ms(2000);

    printf("2st motor test\r\n");
    start_motor();
    Delay_Ms(2000);
    stop_motor();
    Delay_Ms(2000);

    printf("3st motor test\r\n");
    start_motor();
    Delay_Ms(2000);
    stop_motor();
    Delay_Ms(2000);

    printf("4st motor test\r\n");
    start_motor();
    Delay_Ms(2000);
    stop_motor();
    Delay_Ms(2000);

    printf("5st motor test\r\n");
    start_motor();
    Delay_Ms(2000);
    stop_motor();
    Delay_Ms(2000);

    printf("6st motor test\r\n");
    start_motor();
    Delay_Ms(2000);
    stop_motor();
    Delay_Ms(2000);

    printf("7st motor test\r\n");
    start_motor();
    Delay_Ms(2000);
    stop_motor();
    Delay_Ms(2000);

    printf("8st motor test\r\n");
    start_motor();
    Delay_Ms(2000);
    stop_motor();
    Delay_Ms(2000);

    printf("9st motor test\r\n");
    start_motor();
    Delay_Ms(2000);
    stop_motor();
    Delay_Ms(2000);

    printf("10st motor test\r\n");
    start_motor();
    Delay_Ms(2000);
    stop_motor();
    Delay_Ms(2000);

    printf("11st motor test\r\n");
    start_motor();
    Delay_Ms(2000);
    stop_motor();
    Delay_Ms(2000);

    printf("12st motor test\r\n");
    start_motor();
    Delay_Ms(2000);
    stop_motor();
    Delay_Ms(2000);
    */

    //测试通信模块
    /*
    uint8_t TxCnt = 0;
    uint8_t tx_buff[128] = {0};
    tx_buff[0] = '+';
    tx_buff[1] = '+';
    tx_buff[2] = '+';
    tx_buff[3] = '\r';
    tx_buff[4] = '\n';
    while(TxCnt < 5) //发送read_ioin
    {
        while(USART_GetFlagStatus(USART3, USART_FLAG_TXE) == RESET) 
        {
        }
        USART_SendData(USART3, tx_buff[TxCnt++]);
    }
    Delay_Ms(1000);

    while (rx_printf == rx1_cnt) {}
    rx_printf = rx1_cnt;

    if(strstr(RxBuffer1, "Entry AT"))
    {
        TxCnt = 0;
        while(TxCnt < 5) //发送read_ioin
        {
            while(USART_GetFlagStatus(USART3, USART_FLAG_TXE) == RESET) 
            {
            }
            USART_SendData(USART3, tx_buff[TxCnt++]);
        }
        Delay_Ms(1000);
        while (rx_printf == rx1_cnt) {}
        if(strstr(RxBuffer1 + rx_printf, "Power on"))
        {
            printf("com ---SUCCESS---\r\n");
        }
        else {
            printf("com +++FAIL+++\r\n");        
        }
    }
    else if(strstr(RxBuffer1, "Power on"))
    {
        printf("com ---SUCCESS---\r\n");
    }
    else {
        printf("com +++FAIL+++\r\n");    
    }
    printf("\r\n"); 
    */

    rx_printf = rx1_cnt;
    /*

    while(1)
    {
        LORA_ON();
        Delay_Ms(1000);
        while (rx_printf == rx1_cnt) {}
        if(strstr(RxBuffer1 + rx_printf, "Power on"))
        {
            printf("LORA ---SUCCESS---\r\n");
            rx_printf = rx1_cnt;
            break;
        }
        else {
            printf("LORA +++FAIL+++\r\n"); 
            LORA_OFF();
            rx_printf = rx1_cnt;
            Delay_Ms(2000);       
        }

    }
    */

    /* 如果没到位，开电源，到位后转一圈记录霍尔次数 */
    /* 启动时：关电源，检测到位 */
    if (!IsInPosition()) {
        start_motor();
        /* 等待到位 */
        while (!IsInPosition() && motor_running) {
        }
        stop_motor();
        printf("hall_cycle_count1 : %d \r\n", hall_cycle_count);
        printf("hall_cycle_count2 : %d \r\n", hall_cycle_count2);
    }
    
    /* 读取初始霍尔状态并执行一次换相 (确保起始相序正确) */
    //hall_state = read_hall_state();
    //if (hall_state < 8 && hall_to_step_map[hall_state] != 0xFF) {
    //    commutation_step = hall_to_step_map[hall_state];
    //    set_outputs_for_step(commutation_step);
    //} else {
        /* 无效霍尔状态，关闭所有输出 */
    //    all_outputs_off();
    //}
    printf("hall_cycle_count1 : %d \r\n", hall_cycle_count);
    printf("hall_cycle_count2 : %d \r\n", hall_cycle_count2);

   

    while (1) {
        // 读取按钮，按下时切换运行/停止状态 
        bool current_btn_state = GPIO_ReadInputDataBit(BTN_START_PORT, BTN_START_PIN);
        if (last_btn_state && !current_btn_state) {
            Delay_Ms(20);  // 消抖 
            if (!GPIO_ReadInputDataBit(BTN_START_PORT, BTN_START_PIN)) {
                if (!motor_running) 
                {
                    start_motor();
                } else {
                    stop_motor();
                }
            }
        }
        last_btn_state = current_btn_state;

        //看看是不是接收到7字节
        if(rx_printf != rx1_cnt)
        {
            //先延时500ms，避免没接收完成
            Delay_Ms(500);
            printf("rx_printf %u, rx1_cnt %u \r\n", rx_printf, rx1_cnt);
            if(rx1_cnt - rx_printf == 7)
            {
                u8 cmd[7] = {0};
                for(u8 ii = 0; ii < 7; ii++)
                {
                    cmd[ii] = RxBuffer1[rx_printf+ii];
                }
                if(cmd[0] == 0xff)
                {
                    if(cmd[2] == 0x01)
                    {
                        start_motor();
                        Delay_Ms(cmd[4] * 1000);
                        stop_motor();
                    }
                    if(cmd[2] == 0x02)
                    {
                        start_motor();
                        while(senscount < cmd[4])
                        {
                            while (!IsInPosition()){};
                            while (IsInPosition()){};
                            senscount++;
                        }
                        senscount = 0;
                        stop_motor();
                        cmd[3] = cmd[2];
                        cmd[2] = 0x00;
                        cmd[5] = cmd[4];
                        cmd[4] = 0x00;
                        for(u8 ii = 0; ii < 7; ii++)
                        {
                            while(USART_GetFlagStatus(USART3, USART_FLAG_TC) == RESET);
                            USART_SendData(USART3, cmd[ii]);
                        }
                    }
                }
                

            }
            rx_printf = 0;
            rx1_cnt = 0;

        }
        
        Delay_Ms(10);
    }
}
