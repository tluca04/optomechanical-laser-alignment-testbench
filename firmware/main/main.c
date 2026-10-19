#include <stdio.h>
#include "driver/i2c_master.h"
#include "esp_err.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "mpu6050.h"
#include "esp_timer.h"
#include "servo.h"

static const char* TAG = "MAIN";

void app_main(void) {

    i2c_master_bus_config_t bus_config = {
        .i2c_port = I2C_NUM_0,
        .sda_io_num = GPIO_NUM_21,
        .scl_io_num = GPIO_NUM_22,
        .clk_source = I2C_CLK_SRC_DEFAULT,
        .glitch_ignore_cnt = 7,
        .flags.enable_internal_pullup = true,
    };

    i2c_master_bus_handle_t sensor_bus;

    esp_err_t status_mpu650 = i2c_new_master_bus(&bus_config, &sensor_bus);

    if (status_mpu650 != ESP_OK) {
        ESP_LOGE(TAG, "Failed I2C bus initialization: %s", esp_err_to_name(status_mpu650));
        return;
    }

    ESP_LOGI(TAG, "Successful I2C bus initialization");

    i2c_master_dev_handle_t mpu_device;

    status_mpu650 = mpu6050_init(sensor_bus, &mpu_device);
    if (status_mpu650 != ESP_OK) {
        ESP_LOGE(TAG, "Failed MPU6050 initialization");
        return;
    }

    status_mpu650 = mpu6050_test_connection(mpu_device);
    if (status_mpu650 != ESP_OK) {
        ESP_LOGE(TAG, "Failed MPU6050 connection test : %s", esp_err_to_name(status_mpu650));
        return;
    }

    status_mpu650 = mpu6050_configure(mpu_device);
    if (status_mpu650 != ESP_OK) {
        ESP_LOGE(TAG, "Failed MPU6050 configuration: %s", esp_err_to_name(status_mpu650));
        return;
    }

    mpu6050_raw_data_t sensor_data;

    esp_err_t status_servo = servo_init();
    if (status_servo != ESP_OK) {
        ESP_LOGE(TAG, "Failed servo initialization: %s", esp_err_to_name(status_servo));
        return;
    }

    ESP_LOGI(TAG, "Successful servo initialization");


    float pan_angles[] = {0.0f, 90.0f, 180.0f, 90.0f};
    float tilt_angles[] = {0.0f, 90.0f, 180.0f, 90.0f};
    int pan_i = 0;
    int tilt_i = 0;
    bool move_pan = true;

    servo_angle(SERVO_PAN, pan_angles[0]);
    servo_angle(SERVO_TILT, tilt_angles[0]);

    uint32_t last_servo_ms = (uint32_t)(esp_timer_get_time() / 1000);
    TickType_t last_wake_time = xTaskGetTickCount();
    const TickType_t period_ticks = pdMS_TO_TICKS(10);

    while (1) {

        status_mpu650 = mpu6050_read_raw(mpu_device, &sensor_data);
        uint32_t time_ms = (uint32_t)(esp_timer_get_time() / 1000);

        if ((time_ms - last_servo_ms) >= 1000) {
            last_servo_ms += 1000;

            if (move_pan) {
                ++pan_i;
                if (pan_i >= 4) {
                    pan_i = 0;
                }
                servo_angle(SERVO_PAN, pan_angles[pan_i]);

            } else {
                ++tilt_i;
                if (tilt_i >= 4) {
                    tilt_i = 0;
                }
                servo_angle(SERVO_TILT, tilt_angles[tilt_i]);
            }
            move_pan = !move_pan;
        }

        if (status_mpu650 == ESP_OK) {
            printf("DATA,%lu,%d,%d,%d,%d,%d,%d,%d,%.1f,%.1f\n", (unsigned long)time_ms, sensor_data.accel_x, sensor_data.accel_y, sensor_data.accel_z, sensor_data.temp, sensor_data.gyro_x, sensor_data.gyro_y, sensor_data.gyro_z, pan_angles[pan_i], tilt_angles[tilt_i]);
        } else {
            ESP_LOGE(TAG, "Failed MPU6050 read");
        }


        vTaskDelayUntil(&last_wake_time, period_ticks);
    }
}