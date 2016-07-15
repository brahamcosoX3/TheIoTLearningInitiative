#include <errno.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <linux/i2c-dev-user.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdbool.h>

#define RGB_SLAVE       0x62
#define LCD_SLAVE       0x3E
#define BUS             0x06
#define REG_RED         0x04        // pwm2
#define REG_GREEN       0x03        // pwm1
#define REG_BLUE        0x02        // pwm0
#define REG_MODE1       0x00
#define REG_MODE2       0x01
#define REG_OUTPUT      0x08

typedef struct
{
    int addr; //i2c address of device
    int file; //reprsents a place to do the i2c read & write
    int adapter_nr; //the bus number of the device
    char filename[20]; //the name of the device
}I2CCONTEXT;

I2CCONTEXT lcd; //will store the lcd controller context
I2CCONTEXT rgb; //will store the rgb controller context

int initContext(I2CCONTEXT *ctx, int addr_,int bus)
{
    ctx->addr = addr_;
    ctx->adapter_nr = bus;
    snprintf(ctx->filename, 19, "/dev/i2c-%d", ctx->adapter_nr);
    ctx->file = open(ctx->filename, O_RDWR);

    if (ctx->file < 0) 
    {
       /* ERROR HANDLING; you can check errno 2 c what went wrong */
        printf("Error ocurred @ opening BUS: (errno:%d) %s\n",
                errno,
                strerror(errno));
        return -errno;    

    }

    if (ioctl(ctx->file, I2C_SLAVE, ctx->addr) < 0)
    {
        /* ERROR HANDLING; you can check errno 2 c what went wrong */
        printf("Error ocurred @ accessing slave: (errno:%d) %s\n",
                    errno,
                    strerror(errno));
        return -errno;
    }

}

__s32 writeByteRegister(int file, __u8 register_, __u8 value)
{
    __s32 res = -1;
    res = i2c_smbus_write_byte_data(file, register_, value);
    if (res < 0)
    {
        /* ERROR HANDLING: i2c transaction failed */
        printf("Error writing byte, (errno:%d),%s",errno,
                strerror(errno));
    }
}

__s32 readRegister(int register_, int file)
{
    __u8 reg = register_;
    __s32 res = -1;
    char buf[10];  
    res = i2c_smbus_read_word_data(file, reg);
    if (res < 0)
    {
        /* ERROR HANDLING: i2c transaction failed */
        printf("Error reading reg: 0x%x, (errno:%d),%s",
                reg,errno,strerror(errno));
    }
    return res;
}

void setRGBColor(I2CCONTEXT *rgb, int r, int g, int b)
{
    writeByteRegister(rgb->file, REG_RED, r);
    writeByteRegister(rgb->file, REG_GREEN, g);
    writeByteRegister(rgb->file, REG_BLUE, b);            
}

void initRGB(I2CCONTEXT *rgb)
{
    // backlight init
    writeByteRegister(rgb->file, REG_MODE1, 0);
    // set LEDs controllable by both PWM and GRPPWM registers
    writeByteRegister(rgb->file, REG_OUTPUT, 0xFF);
    // set MODE2 values
    writeByteRegister(rgb->file, REG_MODE2, 0x20);
    // set the baklight Color to white :)
    setRGBColor(rgb, 0xFF, 0xFF, 0xFF);    
}

void turnOffRGB(I2CCONTEXT *rgb)
{
    setRGBColor(rgb, 0x00, 0x00, 0x00);    
}

int main()
{
    /*
    we pass a reference to the rgb context variable
    the i2c address of the rgb controller
    and the BUS which should be 1
    */

    initContext(&rgb, RGB_SLAVE , BUS);

    /*turn on RGB LEDS*/
    initRGB(&rgb);
    /*sleep for 5 secs before turning off*/
    sleep(5);
    /*turn off RGB LEDS*/
    turnOffRGB(&rgb);

    printf("\nDONE!\n");

    return 0;
}
