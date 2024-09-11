import time

# Function to control the buzzer
def control_buzzer(BUZZER_PIN, status):
    import RPi.GPIO as GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUZZER_PIN, GPIO.OUT)

    if (status):
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
    else:
        GPIO.output(BUZZER_PIN, GPIO.LOW)


# Function to loop buzzer
def loop_buzzer(BUZZER_PIN, iterations):
    for i in range (0, iterations):
        control_buzzer(BUZZER_PIN, True)
        time.sleep(0.3)
        control_buzzer(BUZZER_PIN, False)
        time.sleep(0.1)


if __name__ == "__main__":
    try:
        import RPi.GPIO as GPIO

        loop_buzzer(16, 5)
    
    except KeyboardInterrupt:
        GPIO.cleanup()