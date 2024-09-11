# Import sensor modules
from sensors import accel, dd_sensor, buzzer, led, dht, mq
import config
import time
import datetime
import threading
import queue
import sqlite3

# Input constants (intervals are measured in seconds)
DHT_PIN = 4
FLAME_PIN = 17
MQ2_COM = "/dev/ttyUSB1"
MQ9_COM = "/dev/ttyUSB0"
COLLECT_DATA_INTERVAL = 0.5
UPLOAD_SQL_INTERVAL = 60

# Output constants
BUZZER_PIN = 16
BUZZER_ITERATIONS = 10
# red and green leds are switched
LED_RED = 6
LED_GREEN = 5
LED_BLUE = 13
LED_ITERATIONS = 3

# Data constants
DATA_QUEUE_SIZE = UPLOAD_SQL_INTERVAL / COLLECT_DATA_INTERVAL
HUMIDITY_MIN = "humidity_min"
HUMIDITY_MAX = "humidity_max"
TEMPERATURE_MAX = "temperature_max"
SHARP_MOVEMENT_THRESHOLD = "sharp_movement_threshold"
MQ_MAX = "mq_max"
DISCORD_WEBHOOK = "discord_webhook"

# Sensor enable control
ENABLE_DHT = "enable_dht"
ENABLE_ACCEL = "enable_accel"
ENABLE_FLAME = "enable_flame"
ENABLE_MQ2 = "enable_mq2"
ENABLE_MQ9 = "enable_mq9"

# Alarm enable control
ENABLE_BUZZER = "enable_buzzer"
ENABLE_LED = "enable_led"

# Create a lock object for synchronized access to sensor_data
data_lock = threading.Lock()


# Sensor data dictionaries for each sensor
# Time will be recorded when writing to the db
sensor_data = {
    "humidity": queue.Queue(),         # humidity (float), temperature (float)
    "acceleration": queue.Queue(),     # delta_x (float), delta_y (float), delta_z (float)
    "flame": queue.Queue(),            # digital_signal (0 - good; 1 - bad)
    "mq2": queue.Queue(),              # digital_signal (0 - bad; 1 - good) !!! changed to analog
    "mq9": queue.Queue(),              # digital_signal (0 - bad; 1 - good) !!! changed to analog
}


# Function to send discord notification
def send_discord_msg(hazard):
    import requests

    if (DISCORD_WEBHOOK not in config.config):
        config.config[DISCORD_WEBHOOK] = 'https://discord.com/api/webhooks/1171770979022807140/P2_cIjQ2UJ0l98Jiobv6r3ssf99rLpleuzfO8OMQWHNAtLC3XHBB9uFbz3woMvvqplEp'
        config.save()

    webhook_url = config.config[DISCORD_WEBHOOK]
    message = {"content": f"**! WARNING !** {hazard.lower().capitalize()} detected!"}
    headers = {
        'Content-Type': 'application/json',
    }
    response = requests.post(webhook_url, json=message, headers=headers)
    if response.status_code == 204:
        print("Message sent successfully")
    else:
        print("Failed to send message")


# Function to read latest data entries from the sensor_data queus without poping the entries
def get_latest_sensor_data_entry():
    data = {}

    with data_lock:

        # DHT
        hum = temp = 0
        i = len(sensor_data["humidity"].queue) - 1
        if (i > -1):
            hum, temp = sensor_data["humidity"].queue[i]
        data["humidity"] = hum
        data["temperature"] = temp
        
        # MPU6050
        val = False
        i = len(sensor_data["acceleration"].queue) - 1
        if (i > -1):
            delta_x, delta_y, delta_z = sensor_data["acceleration"].queue[i]

            if (SHARP_MOVEMENT_THRESHOLD not in config.config):
                config.config[SHARP_MOVEMENT_THRESHOLD] = 15000
                config.save()

            threshold = config.config[SHARP_MOVEMENT_THRESHOLD]
            val = delta_x > threshold or delta_y > threshold or delta_z > threshold
        data["earthquake"] = val

        # Fire sensor
        val = False
        i = len(sensor_data["flame"].queue) - 1
        if (i > -1):
            val = sensor_data["flame"].queue[i] == 1
        data["flame"] = val

        # MQ2
        if (MQ_MAX not in config.config):
            config.config[MQ_MAX] = 500
            config.save()

        val = 0
        i = len(sensor_data["mq2"].queue) - 1
        if (i > -1):
            val = sensor_data["mq2"].queue[i] > config.config[MQ_MAX]
        data["smoke"] = val

        # MQ9
        val = 0
        i = len(sensor_data["mq9"].queue) - 1
        if (i > -1):
            val = sensor_data["mq9"].queue[i] > config.config[MQ_MAX]
        data["gas"] = val
        
        # Time of recording
        data["time"] = get_current_sql_time()
    
    return data


# We will set a maximum queue size of 300
# Sensors will collect data every second -> 5 minutes * 60 seconds = 300 entries
# Data average will be uploaded to the db once every 5 minutes
def ensure_queue_size():
    for key in sensor_data:
        while sensor_data[key].qsize() > DATA_QUEUE_SIZE:
            sensor_data[key].get()


# Function to get the current datetime in sql datetime format
def get_current_sql_time():
    current_time = datetime.datetime.now()
    return current_time.strftime("%Y-%m-%d %H:%M:%S")


# Function to upload the average of collected datat to the db
# The function is tooooo big so another function (below) will be representing the thread
def upload_data_sql():
    # Average values
    avg_humidity = 0
    avg_temperature = 0
    avg_delta_x = 0
    avg_delta_y = 0
    avg_delta_z = 0
    avg_mq2 = 0
    avg_mq9 = 0

    # Values that will indicate if the hazard was detected even once in the time interval between db writes
    # 0 good; 1 bad
    top_flame = 0

    with data_lock:

        # Calculate avg values for the dht sensor
        size_dht = sensor_data["humidity"].qsize()
        if (size_dht == 0): size_dht = 1

        while not sensor_data["humidity"].empty():
            hum, temp = sensor_data["humidity"].get()
            avg_humidity += hum
            avg_temperature += temp
        avg_humidity /= size_dht
        avg_temperature /= size_dht

        # Calculate avg values for the mpu accelerator
        size_mpu = sensor_data["acceleration"].qsize()
        if (size_mpu == 0): size_mpu = 1

        while not sensor_data["acceleration"].empty():
            delta_x, delta_y, delta_z = sensor_data["acceleration"].get()
            avg_delta_x += delta_x
            avg_delta_y += delta_y
            avg_delta_z += delta_z
        avg_delta_x /= size_mpu
        avg_delta_y /= size_mpu
        avg_delta_z /= size_mpu

        # Calculate "top" (most common) value for flame
        flame_one_counter = 0
        size_flame = sensor_data["flame"].qsize()
        if (size_flame == 0): size_flame = 1

        while not sensor_data["flame"].empty():
            val = sensor_data["flame"].get()
            if (val == 1):
                flame_one_counter += 1
        if (flame_one_counter / size_flame >= 0.5):
            top_flame = 1
        else:
            top_flame = 0


        # Calculate avg values for the mq2
        size_mq2 = sensor_data["mq2"].qsize()
        if (size_mq2 == 0): size_mq2 = 1

        while not sensor_data["mq2"].empty():
            avg_mq2 += sensor_data["mq2"].get()
        avg_mq2 /= size_mq2


        # Calculate avg values for the mq9
        size_mq9 = sensor_data["mq9"].qsize()
        if (size_mq9 == 0): size_mq9 = 1

        while not sensor_data["mq9"].empty():
            avg_mq9 += sensor_data["mq9"].get()
        avg_mq9 /= size_mq9


    # Insert into quakeDB.db
    try:
        connection = sqlite3.connect("quakeDB.db")
        cursor = connection.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_data (
                timestamp TIMESTAMP,
                avg_humidity REAL,
                avg_temperature REAL,
                avg_delta_x REAL,
                avg_delta_y REAL,
                avg_delta_z REAL,
                top_flame REAL,
                avg_mq2 REAL,
                avg_mq9 REAL
            )
        ''')

        cursor.execute('''
            INSERT INTO sensor_data (
                timestamp,
                avg_humidity,
                avg_temperature,
                avg_delta_x,
                avg_delta_y,
                avg_delta_z,
                top_flame,
                avg_mq2,
                avg_mq9
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            get_current_sql_time(),
            avg_humidity,
            avg_temperature,
            avg_delta_x,
            avg_delta_y,
            avg_delta_z,
            top_flame,
            avg_mq2,
            avg_mq9
        ))

        connection.commit()
        connection.close()

        print("Success on inserting into quakeDB.db!")
    
    except sqlite3.Error as err:
        print("Failed to insert data into sqlite table", err)
    finally:
        if connection:
            connection.close()
            # print("The sqlite connection is closed")


# Function to read data from the local database
def read_data_sql():
    data_dict = {}

    try:
        connection = sqlite3.connect("quakeDB.db")
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM sensor_data")
        rows = cursor.fetchall()

        col_names = [description[0] for description in cursor.description]

        # initialization
        for col in col_names:
            data_dict[col] = []

        for row in rows:
            for col, value in zip(col_names, row):
                data_dict[col].append(value)

    except sqlite3.Error as err:
        print("Failed to read data from sqlite table", err)
    finally:
        if connection:
            connection.close()
            # print("The sqlite connection is closed")

    return data_dict


# Function to create the upload_data_sql_thread
def upload_data_sql_thread(interval):
    while True:
        time.sleep(interval)
        upload_data_sql()


# Function to trigger the alarm (LED + Buzzer)
def trigger_alarm(hazard):
    send_discord_msg(hazard)
    print("Alarm triggered")

    buzzer_thread = None
    led_thread = None

    if (ENABLE_BUZZER not in config.config):
        config.config[ENABLE_BUZZER] = True
        config.save()

    if (config.config[ENABLE_BUZZER]):
        buzzer_thread = threading.Thread(target=buzzer.loop_buzzer, name="buzzer_thread", args=(BUZZER_PIN, BUZZER_ITERATIONS))
        buzzer_thread.start()

    if (ENABLE_LED not in config.config):
        config.config[ENABLE_LED] = True
        config.save()

    if (config.config[ENABLE_LED]):
        led_thread = threading.Thread(target=led.loop_led, name="led_thread", args=(LED_RED, LED_GREEN, LED_BLUE, LED_ITERATIONS))
        led_thread.start()
    
    # if (enable_buzzer):
    #     buzzer_thread.join()

    # if (enable_led):
    #     led_thread.join()


# Function to read AM2302 data
def read_dht_data(interval):
    # print("Reading dht data...")
    while True:
        if (ENABLE_DHT not in config.config):
            config.config[ENABLE_DHT] = True
            config.save()

        if config.config[ENABLE_DHT]:
            humidity, temperature = dht.read_humidity_temperature(DHT_PIN)
            if humidity is not None and temperature is not None:
                # print("Humidity: ", humidity, " Temperature: ", temperature)

                if (HUMIDITY_MIN not in config.config):
                    config.config[HUMIDITY_MIN] = 30
                    config.save()

                if (HUMIDITY_MAX not in config.config):
                    config.config[HUMIDITY_MAX] = 70
                    config.save()

                if (TEMPERATURE_MAX not in config.config):
                    config.config[TEMPERATURE_MAX] = 50
                    config.save()

                if (humidity < config.config[HUMIDITY_MIN] or 
                    humidity > config.config[HUMIDITY_MAX] or 
                    temperature > config.config[TEMPERATURE_MAX]):
                    print("Dangerous levels of humidity or temperature.")
                    trigger_alarm("Dangerous levels of humidity or temperature")

                with data_lock:
                    sensor_data["humidity"].put((humidity, temperature,))
                    ensure_queue_size()

        time.sleep(interval)


# Function to read MPU6050 data
def read_mpu6050_data(interval):
    # print("Reading accelerator data...")
    # Accelerometer previous values
    prev_acc_x = 0
    prev_acc_y = 0
    prev_acc_z = 0

    while True:
        if (ENABLE_ACCEL not in config.config):
            config.config[ENABLE_ACCEL] = True

        if (config.config[ENABLE_ACCEL]):
            # Note that we don't define pins for the MPU6050 because it can work only with GPIO 2 (SDA) and GPIO 3 (SCL)
            acc_x, acc_y, acc_z = accel.read_raw_acceleration()

            # Calculate changes in acceleration
            delta_x = abs(acc_x - prev_acc_x)
            delta_y = abs(acc_y - prev_acc_y)
            delta_z = abs(acc_z - prev_acc_z)

            # Update accelerometer previous values
            prev_acc_x = acc_x
            prev_acc_y = acc_y
            prev_acc_z = acc_z

            # print("delta_x: ", delta_x, " delta_y: ", delta_y, " delta_z: ", delta_z)

            # Check for sharp movement
            sharp_threshold_passed = False
            if (SHARP_MOVEMENT_THRESHOLD not in config.config):
                config.config[SHARP_MOVEMENT_THRESHOLD] = 15000

            threshold = config.config[SHARP_MOVEMENT_THRESHOLD]
            sharp_threshold_passed = (
                delta_x > threshold 
                or delta_y > threshold 
                or delta_z > threshold
            )

            if sharp_threshold_passed:
                print("Sharp movement detected.")
                trigger_alarm("Sharp movement")

            with data_lock:
                sensor_data["acceleration"].put((
                        delta_x, 
                        delta_y, 
                        delta_z,
                    ))
                ensure_queue_size()
        time.sleep(interval)


# Function to read KY-026 data
def read_flame_data(interval):
    # print("Reading flame data...")
    while True:
        if (ENABLE_FLAME not in config.config):
            config.config[ENABLE_FLAME] = True
            config.save()

        if config.config[ENABLE_FLAME]:
            flame = dd_sensor.read_dd(FLAME_PIN)
            # print('Flame status (0 - good; 1 - bad): ', flame)
            if (flame == 1):
                print("Flame detected.")
                trigger_alarm("Fire")

            with data_lock:
                sensor_data["flame"].put(flame)
                ensure_queue_size()
        time.sleep(interval)


# Function to read MQ-2 data
def read_mq2_data(interval):
    # print("Reading mq2 data...")
    while True:
        if (ENABLE_MQ2 not in config.config):
            config.config[ENABLE_MQ2] = True
            config.save()

        if (config.config[ENABLE_MQ2]):
            mq2 = mq.read_data(MQ2_COM)
            # print('Smoke status: ', mq2)

            if (MQ_MAX not in config.config):
                config.config[MQ_MAX] = 500
                config.save()

            if (mq2 > config.config[MQ_MAX]):
                print("Smoke leakage detected.")
                trigger_alarm("Smoke")
            
            with data_lock:
                sensor_data["mq2"].put(mq2)
                ensure_queue_size()
        time.sleep(interval)


# Function to read MQ-9 data
def read_mq9_data(interval):
    print("Reading mq9 data...")
    while True:
        if (ENABLE_MQ9 not in config.config):
            config.config[ENABLE_MQ9] = True
            config.save()

        if config.config[ENABLE_MQ9]:
            mq9 = mq.read_data(MQ9_COM)
            # print('Gas status: ', mq9)

            if (MQ_MAX not in config.config):
                config.config[MQ_MAX] = 500
                config.save()

            if (mq9 > config.config[MQ_MAX]):
                print("Gas leakage detected.")
                trigger_alarm("Gas")

            with data_lock:
                sensor_data["mq9"].put(mq9)
                ensure_queue_size()
        time.sleep(interval)


def main():
    print("Starting up the threads")
    try:
        dht_thread = threading.Thread(target=read_dht_data, name="dht_thread", args=(COLLECT_DATA_INTERVAL,))
        acceleration_thread = threading.Thread(target=read_mpu6050_data, name="acceleration_thread", args=(COLLECT_DATA_INTERVAL,))
        flame_thread = threading.Thread(target=read_flame_data, name="flame_thread", args=(COLLECT_DATA_INTERVAL,))
        mq2_thread = threading.Thread(target=read_mq2_data, name="mq2_thread", args=(COLLECT_DATA_INTERVAL,))
        mq9_thread = threading.Thread(target=read_mq9_data, name="mq9_thread", args=(COLLECT_DATA_INTERVAL,))
        sql_thread = threading.Thread(target=upload_data_sql_thread, name="sql_thread", args=(UPLOAD_SQL_INTERVAL,))

        dht_thread.start()
        acceleration_thread.start()
        flame_thread.start()
        mq2_thread.start()
        mq9_thread.start()
        sql_thread.start()

    except KeyboardInterrupt:
        dht_thread.join()
        acceleration_thread.join()
        flame_thread.join()
        mq2_thread.join()
        mq9_thread.join()


if __name__ == '__main__':
    main()