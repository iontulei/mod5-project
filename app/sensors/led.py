# Required modules are imported and set up
import time

# The red and green LEDs are inverted on the sensor.
LED_Red = 6 #22
LED_Green = 5 #27
LED_Blue = 13


# Function to control led lights
def control_led(LED_RED, LED_GREEN, LED_BLUE, red_status, green_status, blue_status):
    import RPi.GPIO as GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED_RED, GPIO.OUT)
    GPIO.setup(LED_GREEN, GPIO.OUT)
    GPIO.setup(LED_BLUE, GPIO.OUT)

    GPIO.output(LED_Red, red_status)
    GPIO.output(LED_Green, green_status)
    GPIO.output(LED_Blue, blue_status)


# Function to loop leds in a pattern
def loop_led(LED_RED, LED_GREEN, LED_BLUE, iterations):
    for i in range (0, iterations):
        control_led(LED_RED, LED_GREEN, LED_BLUE, True, False, False)
        time.sleep(0.5)
        control_led(LED_RED, LED_GREEN, LED_BLUE, True, False, True)
        time.sleep(0.5)
        control_led(LED_RED, LED_GREEN, LED_BLUE, False, False, True)
        time.sleep(0.25)
        control_led(LED_RED, LED_GREEN, LED_BLUE, True, True, True)
        time.sleep(0.25)

    control_led(LED_RED, LED_GREEN, LED_BLUE, False, False, False)
  

if __name__ == "__main__":
    import RPi.GPIO as GPIO
    try:
        loop_led(LED_Red, LED_Green, LED_Blue, 3)
        # control_led(17, 27, 22, False, False, False)
    
    # clean up after the program is finished
    except KeyboardInterrupt:
        GPIO.cleanup()