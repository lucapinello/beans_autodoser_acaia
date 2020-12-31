import subprocess as sb
import sys
import time
import random
import pigpio
import numpy as np
import touchphat
import json
from pyacaia import AcaiaScale

GPIO_PIN=15
ACAIA_MAC='00:1C:97:17:FD:97'

sb.call('sudo pigpiod',shell=True)

pi = pigpio.pi()

#cycle the leds
for led in range(1,7):
        touchphat.led_on(led)
        time.sleep(0.25)
        touchphat.led_off(led)
        
        
        
with open('config.json', 'r') as f:
            config = json.load(f)
            stop_speed=config['stop_speed']
            
off_pressed=False            
            
pi.set_servo_pulsewidth(GPIO_PIN, stop_speed)        
        
@touchphat.on_touch("Enter")
def start(event):
    print (event.name, target_weight, manual_mode)
    global dispense
    dispense=True
    touchphat.led_on("Enter")

@touchphat.on_release("Enter")
def start_release(event):
    print ('release start')
    touchphat.led_on("Enter")     
    
@touchphat.on_touch("Back")
def stop(event):
    print (event.name)
    
    global dispense
    global manual_mode
    global stop_speed
    global calibration_idx
    global off_pressed
    
    calibration_stop_speed=[1470,1480,1490,1500]
    
    if not dispense and manual_mode:
        stop_speed=calibration_stop_speed[calibration_idx]
        calibration_idx=(calibration_idx+1)%len(calibration_stop_speed)
        
        config = {'stop_speed': stop_speed}
        with open('config.json', 'w') as f:
            json.dump(config, f)
    
    time.sleep(0.1)
    touchphat.led_off("Back")
    
    dispense=False
    off_pressed=False

@touchphat.on_release("Back")
def stop_release(event):
    print ('release stop')
    touchphat.led_off("Back")  


@touchphat.on_touch("A")
def dose_A(event):
    print (event.name)
    global target_weight
    global manual_mode
    manual_mode=False
    
    target_weight=9
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
    global manual_mode
    manual_mode=False
    
    target_weight=19.5
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
    
    global off_pressed
    
    touchphat.led_on("D")
    touchphat.led_off("A")
    touchphat.led_off("B")
    touchphat.led_off("C")
    time.sleep(0.1)
    
    if off_pressed:
        sb.call('sudo shutdown -h now',shell=True)
    
    off_pressed=True

@touchphat.on_release("D")
def dose_D_release(event):
    touchphat.led_on("D")

    
with open('config.json', 'r') as f:
    config = json.load(f)
    stop_speed=config['stop_speed']


fast_cw=500
mid_cw=300
slow_cw=100

fast_acw=500
mid_acw=280
slow_acw=100
steps_per_direction=80
steps_per_direction_no_weight=15

tolerance=0.08

calibration_idx=0
    
target_weight=9


current_speeds_cw=[stop_speed-fast_cw,stop_speed-mid_cw,stop_speed-slow_cw]
current_speeds_acw=[stop_speed+fast_acw,stop_speed+mid_acw,stop_speed+slow_acw]
current_speeds=current_speeds_cw

manual_mode=False
dispense=False
touchphat.led_on("A")

while True:
    
    direction=1
    n_steps=0
    
    if dispense and manual_mode: #this is helpful to unload the dispenser
        
        touchphat.led_on("Enter")
        
        while dispense:
            
            n_steps+=1
            pi.set_servo_pulsewidth(GPIO_PIN, current_speeds[0])
                
            if n_steps==steps_per_direction_no_weight:

                if direction==1:
                    current_speeds=current_speeds_acw
                else:
                    current_speeds=current_speeds_cw

                direction=direction*-1
                n_steps=0
            
            time.sleep(0.1)
        
        
        #we need this to update things on the fly
        #with open('config.json', 'r') as f:
        #    config = json.load(f)
        #    stop_speed=config['stop_speed']
        #    fast_cw=stop_speed-500
        #    mid_cw=stop_speed-200
        #    slow_cw=stop_speed-80

        #    fast_acw=stop_speed+500
        #    mid_acw=stop_speed+200
        #    slow_acw=stop_speed+80

         #   current_speeds_cw=[fast_cw,mid_cw,slow_cw]
         #   current_speeds_acw=[fast_acw,mid_acw,slow_acw]
         #   current_speeds=current_speeds_cw
        
        pi.set_servo_pulsewidth(GPIO_PIN, stop_speed)  
        touchphat.led_off("Enter")
            
    elif dispense: #here we use the scale
        
        touchphat.led_on("Enter")
        
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
                    
                    if current_weight<target_weight-2.0:
                        pi.set_servo_pulsewidth(GPIO_PIN, current_speeds[0])
                    elif current_weight<=target_weight-1.2:
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
            
            #we need this to update things on the fly
            #with open('config.json', 'r') as f:
            #    config = json.load(f)
            #    stop_speed=config['stop_speed']
            #    fast_cw=stop_speed-500
            #    mid_cw=stop_speed-200
            #    slow_cw=stop_speed-80

            #    fast_acw=stop_speed+500
            #    mid_acw=stop_speed+200
            #    slow_acw=stop_speed+80

            #    current_speeds_cw=[fast_cw,mid_cw,slow_cw]
            #    current_speeds_acw=[fast_acw,mid_acw,slow_acw]
            #    current_speeds=current_speeds_cw
                
                
            pi.set_servo_pulsewidth(GPIO_PIN, stop_speed)  
            
            if scale.device:
                scale.disconnect()
                del scale
            
            dispense=False

        except Exception as e:
            print (e)
            dispense=False

        finally:
            pi.set_servo_pulsewidth(GPIO_PIN, stop_speed)  
            touchphat.led_off("Enter")
            dispense=False
    else:
        #we need this to update things on the fly
        with open('config.json', 'r') as f:
            config = json.load(f)
            try:
                stop_speed=config['stop_speed']
            except:
                pass
            current_speeds_cw=[stop_speed-fast_cw,stop_speed-mid_cw,stop_speed-slow_cw]
            current_speeds_acw=[stop_speed+fast_acw,stop_speed+mid_acw,stop_speed+slow_acw]
            current_speeds=current_speeds_cw
        
        pi.set_servo_pulsewidth(GPIO_PIN, stop_speed)
        time.sleep(0.1)
        
        
        
