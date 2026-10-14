#pragma once

#include "driver/i2c_master.h"
#include "esp_err.h"

#define MPU6050_I2C_ADDRESS 0x68
#define MPU6050_REG_WHO_AM_I 0x75
#define MPU6050_CHIP_ID 0x72
#define MPU6050_REG_PWR_MGMT_1 0x6B
#define MPU6050_REG_ACCEL_XOUT_H 0x3B
#define MPU6050_REG_SPEED_DIV 0x19
#define MPU6050_CONFIG 0x1A
#define MPU6050_GYRO_CONFIG 0x1B
#define MPU6050_ACCEL_CONFIG 0x1C

typedef struct {
    int16_t accel_x;
    int16_t accel_y;
    int16_t accel_z;
    int16_t temp;
    int16_t gyro_x;
    int16_t gyro_y;
    int16_t gyro_z;
} mpu6050_raw_data_t;

esp_err_t mpu6050_init(i2c_master_bus_handle_t bus_handle, i2c_master_dev_handle_t* dev_handle);

esp_err_t mpu6050_test_connection(i2c_master_dev_handle_t dev_handle);

esp_err_t mpu6050_configure(i2c_master_dev_handle_t dev_handle);

esp_err_t mpu6050_read_raw(i2c_master_dev_handle_t dev_handle, mpu6050_raw_data_t* raw_data);