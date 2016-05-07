#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/module.h>

#define BUF_LEN 10

static char name[BUF_LEN];
module_param_string(nombre, name, BUF_LEN, 0);

static int module_init_function(void)
{
    printk(KERN_INFO "Module? Hello! %s\n", name);
    return 0;
}

static void module_exit_function(void)
{
    printk(KERN_INFO "Module? Bye!\n");
}

MODULE_LICENSE("GPL");
MODULE_AUTHOR("xe1gyq");
MODULE_DESCRIPTION("My First Linux Kernel Module");

module_init(module_init_function);
module_exit(module_exit_function);
