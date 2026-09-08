#include "stm32f407xx.h"

void SystemInit(void)
{
#if (__FPU_PRESENT == 1) && (__FPU_USED == 1)
    SCB->CPACR |= ((3UL << (10 * 2)) | (3UL << (11 * 2)));
#endif
}

int main(void)
{
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOEEN;

    GPIOE->MODER &= ~GPIO_MODER_MODER1;
    GPIOE->MODER |= GPIO_MODER_MODER1_0;

    GPIOE->BSRR = GPIO_BSRR_BS1;

    while (1)
    {
        for (volatile uint32_t i = 0; i < 1000000; i++)
            ;
        GPIOE->ODR ^= GPIO_ODR_ODR_1;
    }
}