#include <alt_types.h>
#include <unistd.h>
#include "system.h"
#include "altera_avalon_pio_regs.h"
#include "sys/alt_stdio.h"

alt_u8 toHex(alt_u8 val) {
	if (val < 10) return '0' + val;
	else return ('a' - 10) + val;
}

void printAlt16(const alt_16 val) {
	alt_putchar(toHex((val & 0xf000) >> 12));
	alt_putchar(toHex((val & 0x0f00) >> 8));
	alt_putchar(toHex((val & 0x00f0) >> 4));
	alt_putchar(toHex(val & 0x000f));
}

int main()
{ 
  alt_putstr("Starting!\n");

  /*alt_32 x_read;
  alt_up_accelerometer_spi_dev* acc_dev;
  acc_dev = alt_up_accelerometer_spi_open_dev("/dev/accelerometer_spi");
  if (acc_dev == NULL) { // if return 1, check if the spi ip name is "accelerometer_spi"
      return 1;
  }*/

  while (1) {
	  /*alt_16 val_x = IORD_ALTERA_AVALON_PIO_DATA(FILTER_X_BASE);
	  alt_16 val_y = IORD_ALTERA_AVALON_PIO_DATA(FILTER_Y_BASE);
	  alt_16 val_z = IORD_ALTERA_AVALON_PIO_DATA(FILTER_Z_BASE);
	  alt_printf("%x %x %x\n", val_x, val_y, val_z);*/
	  alt_16 val = IORD_ALTERA_AVALON_PIO_DATA(FILTER_X_BASE);
	  printAlt16(val);
	  val = IORD_ALTERA_AVALON_PIO_DATA(FILTER_Y_BASE);
	  printAlt16(val);
	  val = IORD_ALTERA_AVALON_PIO_DATA(FILTER_Z_BASE);
	  printAlt16(val);
	  alt_putchar('\n');
	  usleep(1000);
  }

  return 0;
}
