#pragma once

#include "esp_err.h"
#include <stdint.h>
#include <stdbool.h>

#define SERVO_GPIO 25
#define SERVO_FREQ_HZ 50
#define SERVO_MIN_PULSE_US 500
#define SERVO_MAX_PULSE_US 2500
#define SERVO_PERIOD_US 20000
#define SERVO_MAX_ANGLE_DEG 180.0f
#define SERVO_MAX_STEPS 16384

esp_err_t servo_init(void);

esp_err_t servo_angle(float angle_degree);