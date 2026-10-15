#include "mpu6050.h"
#include "driver/i2c_master.h"
#include "esp_log.h"

static const char* TAG = "MPU6050";

esp_err_t mpu6050_init(i2c_master_bus_handle_t bus_handle, i2c_master_dev_handle_t* dev_handle) {

    i2c_device_config_t dev_config = {
        .dev_addr_length = I2C_ADDR_BIT_LEN_7,
        .device_address = MPU6050_I2C_ADDRESS,
        .scl_speed_hz = 400000,
    };

    esp_err_t status = i2c_master_bus_add_device(bus_handle, &dev_config, dev_handle);

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

esp_err_t mpu6050_configure(i2c_master_dev_handle_t dev_handle) {

    uint8_t i2cpack[5][2] = {{MPU6050_REG_PWR_MGMT_1, 0x01}, {MPU6050_CONFIG, 0x03}, {MPU6050_REG_SPEED_DIV, 0x09}, {MPU6050_GYRO_CONFIG, 0x00}, {MPU6050_ACCEL_CONFIG, 0x00}};

    for (int i = 0; i < 5; ++i) {

        esp_err_t status = i2c_master_transmit(dev_handle, i2cpack[i], sizeof(i2cpack[i]), 50);

        if (status != ESP_OK) {
            ESP_LOGE(TAG, "Failed MPU6050 configuration at index %d", i);
            return status;
        }
    }
    ESP_LOGI(TAG, "Succesful MPU6050 configuration");
    return ESP_OK;
}

esp_err_t mpu6050_read_raw(i2c_master_dev_handle_t dev_handle, mpu6050_raw_data_t* raw_data) {

    if (raw_data == NULL) {
        ESP_LOGE(TAG, "Invalid pointer argument");
        return ESP_ERR_INVALID_ARG;
    }

    uint8_t reg = MPU6050_REG_ACCEL_XOUT_H;

    uint8_t data[14];

    esp_err_t status = i2c_master_transmit_receive(dev_handle, &reg, 1, data, sizeof(data), 50);

    if (status != ESP_OK) {
        ESP_LOGE(TAG, "Failed I2C read: %s", esp_err_to_name(status));
        return status;
    }

    raw_data->accel_x = (int16_t)((data[0] << 8) | data[1]);
    raw_data->accel_y = (int16_t)((data[2] << 8) | data[3]);
    raw_data->accel_z = (int16_t)((data[4] << 8) | data[5]);
    raw_data->temp = (int16_t)((data[6] << 8) | data[7]);
    raw_data->gyro_x = (int16_t)((data[8] << 8) | data[9]);
    raw_data->gyro_y = (int16_t)((data[10] << 8) | data[11]);
    raw_data->gyro_z = (int16_t)((data[12] << 8) | data[13]);

    return ESP_OK;
}