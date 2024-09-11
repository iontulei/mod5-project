import Adafruit_DHT as DHT
import sys
import time

def read_humidity_temperature(DHT22_PIN):
    humidity, temperature = DHT.read_retry(DHT.DHT22, DHT22_PIN)

    humidity = round(humidity, 2)
    temperature = round(temperature, 2)

    return humidity, temperature


if __name__ == "__main__":
    try:
        while True:
            # humidity, temperature = DHT.read_retry(DHT.DHT22, 4)
            humidity, temperature = read_humidity_temperature(4)
            
            if humidity is not None and temperature is not None:
                print('Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity))
            else:
                print('Failed to get reading from ASM2302.')
            
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        sys.exit(1)