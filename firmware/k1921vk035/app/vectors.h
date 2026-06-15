#include "K1921VK035.h"

void chip_init();

typedef void (*IntFunc) (void);

void _start();

#define VECTORS_COUNT 48

extern IntFunc exception_table[VECTORS_COUNT];
