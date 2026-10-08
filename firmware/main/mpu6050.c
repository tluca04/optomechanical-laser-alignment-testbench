#include "mpu6050.h"
#include "esp_log.h"

static const char* TAG = "MPU6050";

esp_err_t mpu6050_init(i2c_master_bus_handle_t bus_handle, i2c_master_dev_handle_t* dev_handle) {

    i2c_device_config_t dev_cfg = {
        .dev_addr_length = I2C_ADDR_BIT_LEN_7,
        .device_address = MPU6050_I2C_ADDRESS,
        .scl_speed_hz = 400000,
    };

    esp_err_t status = i2c_master_bus_add_device(bus_handle, &dev_cfg, dev_handle);

    if (status != ESP_OK) {
        ESP_LOGE(TAG, "Failed to attach MPU6050 device to bus: %s", esp_err_to_name(status));
        return status;
    }

    ESP_LOGI(TAG, "Succesful MPU6050 device attachement");
    return ESP_OK;
}

esp_err_t mpu6050_test_connection(i2c_master_dev_handle_t dev_handle) {

    uint8_t reg = MPU6050_REG_WHO_AM_I;
    uint8_t data = 0;

    esp_err_t status = i2c_master_transmit_receive(dev_handle, &reg, 1, &data, 1, 50);

    if (status != ESP_OK) {
        ESP_LOGE(TAG, "Failed I2C communication: %s", esp_err_to_name(status));
        return status;
    }

    if (data != MPU6050_CHIP_ID) {
        ESP_LOGE(TAG, "Unknown device ID: 0x%02X", data);
        return ESP_ERR_NOT_FOUND;
    }

    ESP_LOGI(TAG, "MPU6050 connection verified");
    return ESP_OK;
}