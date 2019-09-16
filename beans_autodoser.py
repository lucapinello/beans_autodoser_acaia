import subprocess as sb
import sys
import time
import random
import pigpio
import numpy as np
import touchphat
from pyacaia import AcaiaScale

GPIO_PIN=15
ACAIA_MAC='00:1C:97:17:FD:97'
stop_speed=1490
target_weight=10

sb.call('sudo pigpiod',shell=True)

pi = pigpio.pi()

#cycle the leds
for led in range(1,7):
        touchphat.led_on(led)
        time.sleep(0.25)
        touchphat.led_off(led)

pi.set_servo_pulsewidth(GPIO_PIN, stop_speed)        
        
@touchphat.on_touch("Enter")
def start(event):
    
    print (event.name, target_weight)
    global dispense
    dispense=True
    touchphat.led_on("Enter")
   

@touchphat.on_release("Enter")
def start_release(event):
    print ('release start')
    touchphat.led_off("Enter")     
    
@touchphat.on_touch("Back")
def stop(event):
    print (event.name)
    
    global dispense
    global manual_mode
    
    dispense=False
    manual_mode=False

@touchphat.on_release("Back")
def stop_release(event):
    print ('release stop')
    touchphat.led_off("Back")  


@touchphat.on_touch("A")
def dose_A(event):
    print (event.name)
    global target_weight
    
    target_weight=10
    time.sleep(0.1)
    touchphat.led_on("A")
    touchphat.led_off("B")
    touchphat.led_off("C")
    touchphat.led_off("D")

@touchphat.on_release("A")
def dose_A_release(event):
    touchphat.led_on("A")

@touchphat.on_touch("B")
def dose_B(event):
    print (event.name)
    global target_weight
    
    target_weight=20
    time.sleep(0.1)
    touchphat.led_on("B")
    touchphat.led_off("A")
    touchphat.led_off("C")
    touchphat.led_off("D")

@touchphat.on_release("B")
def dose_B_release(event):
    touchphat.led_on("B")
 
@touchphat.on_touch("C")
def dose_C(event):
    print (event.name)
    
    global manual_mode
    manual_mode=True
    
    #target_weight=100
    time.sleep(0.1)
    touchphat.led_on("C")
    touchphat.led_off("A")
    touchphat.led_off("B")
    touchphat.led_off("D")

@touchphat.on_release("C")
def dose_C_release(event):
    touchphat.led_on("C")
    
@touchphat.on_touch("D")
def dose_D(event):
    print (event.name)
    touchphat.led_on("D")
    touchphat.led_off("A")
    touchphat.led_off("B")
    touchphat.led_off("C")
    time.sleep(0.1)
    sb.call('sudo shutdown -h now',shell=True)

@touchphat.on_release("D")
def dose_D_release(event):
    touchphat.led_on("D")


stop_speed=1490
target_weight=10
steps_per_direction=15
tolerance=0.15
current_speeds_cw=[1100,1250,1400]
current_speeds_acw=[1800,1700,1550]
current_speeds=current_speeds_cw

manual_mode=False
dispense=False
touchphat.led_on("A")

while True:
    
    direction=1
    n_steps=0
    
    if dispense and manual_mode: #this is helpful to unload the dispenser
        
        while manual_mode:
            
            n_steps+=1
            pi.set_servo_pulsewidth(GPIO_PIN, current_speeds[0])
                
            if n_steps==steps_per_direction:

                if direction==1:
                    current_speeds=current_speeds_acw
                else:
                    current_speeds=current_speeds_cw

                direction=direction*-1
                n_steps=0
            time.sleep(0.1)

        dispense=False
        pi.set_servo_pulsewidth(GPIO_PIN, stop_speed)  
        
    
    elif dispense: #here we use the scale
        

        try:
            scale=AcaiaScale(mac=ACAIA_MAC)
            scale.connect()
            time.sleep(0.5)
            scale.tare()
            time.sleep(0.5)
        except:
            print ('Scale not available')
            touchphat.led_off("Enter")
            continue

        
        current_weight=0.0


        print ('START')   
        try:
            while current_weight<(target_weight-tolerance) and dispense and scale.device:
                    
                if scale.device.waitForNotifications(1.0):
                    
                    current_weight=scale.weight
                    
                    if current_weight is None:
                        current_weight=0.0
                        continue
                        
                    n_steps+=1
                    
                    if current_weight<target_weight-2:
                        pi.set_servo_pulsewidth(GPIO_PIN, current_speeds[0])
                    elif current_weight<=target_weight-1:
                        pi.set_servo_pulsewidth(GPIO_PIN, current_speeds[1])
                    else:
                        pi.set_servo_pulsewidth(GPIO_PIN, current_speeds[2])


                if n_steps==steps_per_direction:
                    #print (current_weight,direction)
                    if direction==1:
                        current_speeds=current_speeds_acw
                    else:
                        current_speeds=current_speeds_cw

                    direction=direction*-1
                    n_steps=0

                current_weight=scale.weight


            pi.set_servo_pulsewidth(GPIO_PIN, stop_speed)  
            
            if scale.device:
                scale.disconnect()
            
            dispense=False

        except Exception as e:
            print (e)
            dispense=False

        finally:
            pi.set_servo_pulsewidth(GPIO_PIN, stop_speed)  
            touchphat.led_off("Enter")
            dispense=False
    else:
        time.sleep(0.1)
        
        
        
