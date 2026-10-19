#include "servo.h"
#include <stdint.h>
#include "driver/ledc.h"
#include "esp_check.h"
#include "hal/ledc_types.h"
#include "soc/clk_tree_defs.h"
#include "esp_log.h"

static const char* TAG = "SG90";

esp_err_t servo_init(void) {

    ledc_timer_config_t timer_config = {
        .speed_mode = LEDC_LOW_SPEED_MODE,
        .duty_resolution = LEDC_TIMER_14_BIT,
        .timer_num = LEDC_TIMER_0,
        .freq_hz = SERVO_FREQ_HZ,
        .clk_cfg = LEDC_AUTO_CLK,
    };

    ledc_channel_config_t channel_config_pan = {
        .gpio_num = SERVO_GPIO_PAN,
        .speed_mode = LEDC_LOW_SPEED_MODE,
        .channel = LEDC_CHANNEL_0,
        .timer_sel = LEDC_TIMER_0,
        .duty = 0,
        .hpoint = 0,
    };

    ledc_channel_config_t channel_config_tilt = {
        .gpio_num = SERVO_GPIO_TILT,
        .speed_mode = LEDC_LOW_SPEED_MODE,
        .channel = LEDC_CHANNEL_1,
        .timer_sel = LEDC_TIMER_0,
        .duty = 0,
        .hpoint = 0,
    };

    ESP_RETURN_ON_ERROR(ledc_timer_config(&timer_config), TAG, "Failed timer config");
    ESP_RETURN_ON_ERROR(ledc_channel_config(&channel_config_pan), TAG, "Failed channel pan config");
    ESP_RETURN_ON_ERROR(ledc_channel_config(&channel_config_tilt), TAG, "Failed channel tilt config");

    ESP_LOGI(TAG, "Succesful SG90 configuration on GPIO %d", SERVO_GPIO_PAN);
    return ESP_OK;
}


esp_err_t servo_angle(servo_axis_t axis, float angle_degree) {

    if ((axis != SERVO_PAN) && (axis != SERVO_TILT)) {
        ESP_LOGE(TAG, "Axis is neither the SERVO PAN and SERVO TILT");
        return ESP_ERR_INVALID_ARG;
    }

    if (angle_degree < 0.0f) {
        angle_degree = 0.0f;
        ESP_LOGW(TAG, "SG90 angle fixed (below 0°)");
    } else if (angle_degree > SERVO_MAX_ANGLE_DEG) {
        angle_degree = SERVO_MAX_ANGLE_DEG;
        ESP_LOGW(TAG, "SG90 angle fixed (above 180°)");
    }

    float pulse_us = SERVO_MIN_PULSE_US + (angle_degree / SERVO_MAX_ANGLE_DEG) * (SERVO_MAX_PULSE_US - SERVO_MIN_PULSE_US);

    uint32_t duty = (pulse_us / SERVO_PERIOD_US) * SERVO_MAX_STEPS;

    ESP_RETURN_ON_ERROR(ledc_set_duty(LEDC_LOW_SPEED_MODE, (ledc_channel_t)axis, duty), TAG, "Failed to set duty");
    ESP_RETURN_ON_ERROR(ledc_update_duty(LEDC_LOW_SPEED_MODE, (ledc_channel_t)axis), TAG, "Failed to Update duty");

    return ESP_OK;
}