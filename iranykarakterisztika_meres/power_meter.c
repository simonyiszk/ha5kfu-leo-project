#include <stdio.h>
#include <stdint.h>
#include <unistd.h>
#include <complex.h>
#include <math.h>
#include <time.h>

#define DC 127.5

#define sample_rate 1000000
#define freq_offset 200000
#define N_OUTPUTS 5

#define lo_size (sample_rate / freq_offset)

complex float cnco() {

    static complex float lo[lo_size];
    static uint8_t loindex = 0;

    static int init_done = 0;
    if (!init_done) {
        for (int i = 0; i<lo_size; i++) {
            lo[i] = cexp(-I*2.0*M_PI*i / lo_size);
        }
        init_done = 1;
    }


    complex float val = lo[loindex];
    loindex = (loindex + 1) % lo_size;
    return val;
}



const uint32_t dec_factor = sample_rate;
int decimate(float in, float *out) {
    static float dec_acc = 0;
    static uint32_t dec_index = 0;
    dec_acc += in;
    dec_index = (dec_index + 1) % dec_factor;
    if (!dec_index) {
        *out = dec_acc / dec_factor;
        dec_acc = 0;
        return 1;
    }
    return 0;
}


int main() {
    int skipped_bytes = 0;
    long int num_outputs = 0;
    while (1) {
        uint8_t in[2];
        int k = fread(in, 1, 2, stdin);
        if (feof(stdin)) {
            printf("FEOF\n");
            break;
        }
        if (k!=2) {
            usleep(10000);
            continue;
        }
        // skip initaial dongle info struct
        if (skipped_bytes < 12) {
            skipped_bytes += 2;
            continue;
        }
        complex float z = (in[0]-DC)/DC + I*(in[1]-DC)/DC;
        z = z * cnco();
        z = z * conj(z);
        float decout;
        if (decimate(creal(z),&decout)) {
            printf("%ld,%f\n", time(NULL), decout);
            //printf("%ld,%e\n", num_outputs, decout);
            fflush(stdout);
            num_outputs++;
        }
    }
    close(fileno(stdin));
    fflush(stdin);
    //printf("power meter OUT\n");
    return 0;
}
