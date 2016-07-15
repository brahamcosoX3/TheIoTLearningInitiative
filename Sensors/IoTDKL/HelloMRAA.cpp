#include "mraa.h"

int main(int argc, char** argv) {
	const char* board_name = mraa_get_platform_name();
	int i2c_bus, i, i2c_adapter;

	fprintf(stdout, "hello mraa\n Version: %s\n Running on %s\n", mraa_get_version(), board_name);
	mraa_deinit();

	return MRAA_SUCCESS;
}
