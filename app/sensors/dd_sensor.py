# A general script to read data from digital sensors (such as the flame sensor a the MQ sensors)

def read_dd(INPUT_PIN):
    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(INPUT_PIN, GPIO.IN)

    input = GPIO.input(INPUT_PIN)
    # print('DD signal for GPIO ' , INPUT_PIN, ': ', input)
    return input


if __name__ == "__main__":
    import time
    import sys

    try:
        while True:
            # flame = read_dd(17)
            # print("flame: ", flame)

            mq2 = read_dd(27)
            print("mq2: ", mq2)

            # mq9 = read_dd(22)
            # print("mq9: ", mq9)
            
            time.sleep(1)

    except KeyboardInterrupt:
        sys.exit(1)