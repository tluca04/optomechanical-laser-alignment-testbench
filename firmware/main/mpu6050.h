#pragma once

#include "driver/i2c_master.h"
#include "esp_err.h"

#define MPU6050_I2C_ADDRESS 0x68
#define MPU6050_REG_WHO_AM_I 0x75
#define MPU6050_CHIP_ID 0x72

esp_err_t mpu6050_init(i2c_master_bus_handle_t bus_handle, i2c_master_dev_handle_t *dev_handle);

esp_err_t mpu6050_test_connection(i2c_master_dev_handle_t dev_handle);