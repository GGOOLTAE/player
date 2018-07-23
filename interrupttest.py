import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def my_callback(channel):
    print("Key(20) Pressed")
    
GPIO.add_event_detect(20, GPIO.FALLING, callback=my_callback)

try:
    print("Waiting f or falling edge on port 21")
    GPIO.wait_for_edge(21, GPIO.RISING)
    print("Falling edge detected. Here endeth the second lesson.")

except KeyboardInterrupt:
    print('k
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit
    
print ('a')
GPIO.cleanup()           # clean up GPIO on normal exit
