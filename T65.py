"""
Name:    T-65 X-Wing Fighter Sound Simulator
Purpose: Kickass Xmas gift for my son James
Works with pyhton3.4 and python2.7
Thanks to Prasaanth for the help! :-)
"""

#the next line is only needed for python2.x and not necessary for python3.x
from __future__ import print_function, division

import pygame
import os
import sys
import glob
import random
import threading
import time
from random import randint
from threading import Timer
from threading import Thread


# Initiate Global Flags & States
aux_mode_timer_dict = dict() 
power_mode_timer_dict = dict() 
timeElapsed = 0 #used for random delays
master_lock_on = True
aux_power_on = False
main_power_on = False
engine_started = False
weapons_armed = False
landing_gear_down = True
weapon_selected = 1
foil_position_closed = True

gpio_27_flag = False # remove later, just for GPIO Tests & Sample

# Initiate display window, required to collect key board input
game_display = pygame.display.set_mode((800, 600))
#xwing_image = pygame.image.load('xwing.png')
pygame.display.set_caption('T-65 Simulator')
game_display.fill((0,0,0)) 
#sys_font = pygame.font.SysFont("monospace",30)  #need a font file
#game_display.blit(xwing_image,(350,300))

# initiate sound mixer
pygame.mixer.pre_init(44100, -16, 2, 2048) # setup mixer to avoid sound lag (try reducing/increasing last number default is 3072)
pygame.mixer.init()
pygame.init()

# Initiate the Joystick
stick = pygame.joystick.Joystick(0)
stick.init()
joystick_count = pygame.joystick.get_count()    # get number of joysticks
print("Joystick count:",joystick_count)
print("initialized:",bool(stick.get_init()))
print(stick.get_name())
print("initialized:",bool(stick.get_init()))
print(stick.get_name())

# if using python2, the get_input command needs to act like raw_input:
if sys.version_info[:2] <= (2, 7):
    get_input = raw_input
else:
    get_input = input # python3


# load sounds files
engine_sound = pygame.mixer.Sound('sounds/engine.wav')
laser1_sound = pygame.mixer.Sound('sounds/laser1.wav')
laser2_sound = pygame.mixer.Sound('sounds/laser2.wav')
laser3_sound = pygame.mixer.Sound('sounds/laser3.wav')
weapons_armed_sound = pygame.mixer.Sound('sounds/weapons_armed.wav')
alarm_sound = pygame.mixer.Sound('sounds/alarm_02.wav')
torpedo_sound = pygame.mixer.Sound('sounds/torpedo.wav') 
button_press_sound = pygame.mixer.Sound('sounds/button_press.wav') 
button_press_sound.set_volume(.2)
acknowledge_sound = pygame.mixer.Sound('sounds/acknowledge.wav')
error_sound = pygame.mixer.Sound('sounds/error.wav')
microphone_on_sound = pygame.mixer.Sound('sounds/mic_static.wav')  
hyperdrive_sound = pygame.mixer.Sound('sounds/hyperdrive.wav')  
start_engine_sound = pygame.mixer.Sound('sounds/startengine.wav')
aux_power_on_sound = pygame.mixer.Sound('sounds/aux_power_on.wav')  
aux_power_off_sound = pygame.mixer.Sound('sounds/aux_power_off.wav')
engine_shutdown_sound = pygame.mixer.Sound('sounds/engine_shutdown.wav')
xwing_turn_sound = pygame.mixer.Sound('sounds/xwing_turn.wav') 
xwing_turn_sound.set_volume(.3)
#failed_start_engine_sound = # Add randomly failed starts!
foil_sound = pygame.mixer.Sound('sounds/foil.wav')  #UPDATE WITH BETTER FOIL SOUND or make louder ???*****
landing_gear_sound = pygame.mixer.Sound('sounds/landing_gear.wav') 
landing_sound = pygame.mixer.Sound('sounds/landing.wav')

# load groups of sound files
r2_sound_files = glob.glob("sounds/r2d2_*.wav")
chewy_sound_files = glob.glob("sounds/Star_Wars_Soundboard_chew*.wav")
radio_sound_files = glob.glob("sounds/radio_*.wav")
yoda_sound_files = glob.glob("sounds/Star_Wars_Soundboard_yod*.wav")
tie_fighter_sound_files = glob.glob("sounds/Star_Wars_Soundboard_xwtie*.wav")
music_files = glob.glob("sounds/Star_Wars_Soundboard_msc*.wav")

#Configure Channels for Sound that can't overlap, share some of the same channels, if no chance of overlap
#************* FIX - come back and reserve these channels using pygame.mixer.set_reserved
pygame.mixer.set_num_channels(14) # default is 8
start_engine_channel = pygame.mixer.Channel(8)
engine_channel = pygame.mixer.Channel(1)
pygame.mixer.set_reserved(1)
music_channel = pygame.mixer.Channel(10)
pygame.mixer.set_reserved(10)
r2_channel = pygame.mixer.Channel(2) 
radio_channel = pygame.mixer.Channel(3)
tie_fighter_channel = pygame.mixer.Channel(4)
yoda_channel = pygame.mixer.Channel(5)
chewy_channel = pygame.mixer.Channel(6)
hyperdrive_channel = pygame.mixer.Channel(7) 
foil_channel = pygame.mixer.Channel(9)


################################ START OF FLASHY LIGHT SAMPLE CODE ############################
#Flashy Light Code - to control LEDs
class led_flash_thread_class(Thread):
    def __init__(self):
        super(led_flash_thread_class, self).__init__()
        self._keepgoing = True
        self._flashLED = False
        self.aux_power_sequence = False
        self._list_of_pins =  []

    def run(self):
        print("led_flash_thread_class is running")
        while self._keepgoing:
            if self.aux_power_sequence:
                print("start the LED light sequence for when aux_power is turned on")
                # flash the shared pins, then cycle through the function key LEDs 2 at a time...
                #this will continue until the end... even if Aux power is killed, need way to stop While statement immediately...
                #add a check before each new section of start up... to see if Still in Aux Power on... test by stopping Aux power part way through...
                GPIO.output(f1_led_gpio_pin, True)
                GPIO.output(f2_led_gpio_pin, True)
                time.sleep(.5)
                GPIO.output(f1_led_gpio_pin, False)
                GPIO.output(f2_led_gpio_pin, False)
                time.sleep(.5)
                if self.aux_power_sequence: #flash a second time
                    GPIO.output(f1_led_gpio_pin, True)
                    GPIO.output(f2_led_gpio_pin, True)
                    time.sleep(.5)
                    GPIO.output(f1_led_gpio_pin, False)
                    GPIO.output(f2_led_gpio_pin, False)
                    time.sleep(.5)
                self.aux_power_sequence = False #stop this portion of while statement from continuing..
            if self.aux_power_off_sequence:
                print("start the LED light sequence for when aux_power is turned off, flash the lights twice...")
    #************** add LED sequence for off ***********************
            elif self._flashLED:
                GPIO.output(engine_start_led_gpio_pin, True)
                time.sleep(.5)
                GPIO.output(27, False)
                time.sleep(.5)

    def stopflash(self):    #Used for LED Test
        self._flashLED = False
        GPIO.output(27, False)
        print("led_flash_thread_class-stopflash called")

    def startflash(self):
        self._flashLED = True
        print("led_flash_thread_class-flash called")

    def start_aux_power_sequence(self):
        self.aux_power_sequence = True
        print("Start Aux Power Light sequence in separate thread")

    def stop_aux_power_sequence(self):
        self.aux_power_sequence = False
        print("Stop Aux Power Light sequence in separate thread")

    def add_to_list(self,element):
        self._list_of_pins.insert(0, element)
        print("my thread list contains", self._list_of_pins)

    def print_list(self):
        for x in self._list_of_pins:
            print(x)
    
    def remove_from_list(self,element):
        self._list_of_pins.remove(element)
        print("after remove, my list contains", self._list_of_pins)

    def kill(self):
        self._keepgoing = False
        GPIO.output(27, False)


#led_flash_thread = led_flash_thread_class()  # this needs to be initialized... not sure where
#led_flash_thread.start()
#led_flash_thread.add_to_list(21)
#led_flash_thread.add_to_list(22)
#led_flash_thread.print_list()
#led_flash_thread.remove_from_list(22)
#led_flash_thread.print_list()
################################ END OF FLASHY LIGHT SAMPLE CODE ############################


# TO CALL FLASHY LIGHT CODE
#    if running_on_pi:
#        if gpio_27_flag:
#            led_flash_thread.stopflash()
#            gpio_27_flag = False
#        else:
#            gpio_27_flag = True
#            # GPIO.output(27,gpio_27_flag)
#            led_flash_thread.startflash()

#led_flash_tread.starter_begin_flash()



################################ GAME FUNCTIONS ############################

def unlock():
    global master_lock_on

    master_lock_on = True
    print("Master key is ON")
    #check if aux power switch is on position, if so turn on aux_power
    if  aux_power_on: #Aux on
        print("Aux switch is in on position, call aux_power_on func")
        turn_aux_power_on()

def lock():
    global master_lock_on

    master_lock_on = False
    print("Master key is OFF")
    for key in aux_mode_timer_dict: #stop all timers
        print(key)
        timer_task = aux_mode_timer_dict[key]
        timer_task.cancel()
    pygame.mixer.stop()  #stop all sound
    # CHECK IF STARTED IF SO>>> PLAY STOP ENGINE SOUND, OTHERWISE< CHECK IF aux on... etc
    if engine_started:
        stop_engine("lock_off")
    elif aux_power_on:
        turn_aux_power_off()

def turn_aux_power_on():  #Rename this function to turn_aux_power_on_begin and change "aux_power_switch_check" to "aux_power_on_end"
    global aux_power_on

    print("aux_power_on function entered")
    if master_lock_on and not aux_power_on:
        stop_music()
        start_engine_channel.play(aux_power_on_sound)
        #led_flash_tread.starter_begin_flash()
        sound_length = aux_power_on_sound.get_length()
        timer_task = Timer(sound_length+0.5, aux_power_switch_check, ())  # wait till aux on sound is done, then check switches & start the appropriate sounds and set flag
        aux_mode_timer_dict['aux_power_on_TIMER'] = timer_task
        timer_task.start()  #Start timer
    
def aux_power_switch_check(): #called from turn_aux_power_on, check switches & turns on appropriate actions
    global aux_power_on
    #if running_on_pi:
        #if  GPI.input(r2_radio_gpio_pin): #R2 on
        #    print("r2 radio is in on position, call start random r2")
        #    play_r2_with_random_delays()
        #if GPI.input(alliance_radio_gpio_pin): #radio is on
        #    print("alliance radio is in on position, call start random radio")
             #    play_radio_with_random_delays()
        #if GPI.input(arm_weapons_gpio_pin): #Arm Weapons   #Not sure I need to check this as I always maintain a global flag for weapons_armed
        #    print("weapons are in armed position, call arm_weapons")
        #   arm_weapons()     #don't want to do this... engines need to be running. so play armed sound on engine start, not aux_power on
    aux_power_on = True
    print("aux power flag set to True")

def turn_aux_power_off():
    global aux_power_on

    print("aux_power_off")
    #if master_key_on:
    for key in aux_mode_timer_dict: #stop all timers used in Aux Power Mode
        timer_task = aux_mode_timer_dict[key]
        timer_task.cancel()
    for key in aux_mode_timer_dict: #stop all timers in Engine Power Mode
        timer_task = aux_mode_timer_dict[key]
        timer_task.cancel()
    pygame.mixer.stop()  #stop all sound
    # if Engine started, play stop engine sound
    if engine_started:
        print("engine was started, so call stop engine")
        stop_engine("aux_off")
    elif master_lock_on:
        print("engine wasn't started but key is on so play aux_power_off sound")
        #***********add check if channel busy?)
        start_engine_channel.play(aux_power_off_sound)
    aux_power_on = False


def start_engine():
    global engine_started

    print("start_engine func. called")
    if not engine_started and aux_power_on and master_lock_on:
        if not start_engine_channel.get_busy():
            start_engine_channel.play(start_engine_sound, maxtime=4500)
            set_engine_volume()
            engine_channel.play(engine_sound, -1, fade_ms=7000)  # -1 parameter makes it loop non-stop
            print('start 6 second timer to finish off start engine mode')
            timer_task = Timer(6, finish_start_engine,())  # wait 5 secs then call finish_start_engine
            aux_mode_timer_dict['aux_engine_start_TIMER'] = timer_task
            timer_task.start()  # Start timer

def finish_start_engine():
    global engine_started

    if weapons_armed:
        arm_weapons()
    engine_started = True

def set_engine_volume():
    #if stick.get_name()=="Logitech Logitech Extreme 3D":  #only do for Logitech Joystick
    #    pygame.event.pump()
    #    throttle_position = stick.get_axis(3)  # get the current position of an axis
    #    print ("throttle setting: ",throttle_position)
    #    engine_volume = ((1+(-1 * throttle_position)) * .5)+.01 #convert the throttle that goes from +1 to 1 (in reverse), so that it goes from 25% to 100% or set volume expect 0-1 so .5-1
    #    print ("setting volume to: ",engine_volume)
    #    engine_channel.set_volume(engine_volume)
    #	engine_sound.set_volume(engine_volume)
    #   else:
    engine_sound.set_volume(.25)
    engine_channel.set_volume(.25)

def stop_engine(stop_mode):
    global engine_started

    if engine_started: #only stop if already started
        if stop_mode == "landing":
            engine_channel.fadeout(3000)
            landing_sound.play()
        else: 				# "aux_off or key_off, do same for both
            engine_channel.play(engine_shutdown_sound)
        engine_started = False
        for key in power_mode_timer_dict: #stop all timers in Engine Power Mode
            timer_task = power_mode_timer_dict[key]
            timer_task.cancel()
        #Add Stop any sounds that can only play when engine is engaged!*****new tie fighters should be stopped by killing timer above, stop hyperdrive?
        
def land_xwing():
    global engine_started

    print("land_xwing function entered")
    if engine_started:
        if landing_gear_down:
            stop_engine("landing")
        else:
            error_sound.play()

def toggle_music():
    print('play_music function entered.')
    if aux_power_on:
        if not music_channel.get_busy():
            print("not busy")
            soundwav = random.choice(music_files)
            musicsound1 = pygame.mixer.Sound(soundwav)
            music_channel.play(musicsound1)
        else:
            music_channel.stop()

def stop_music():
# initialize music & volume - need to preload with all music
    print('stop_music function entered')
    music_channel.stop()

def play_r2_with_random_delays():
    global aux_mode_timer_dict
    global timeElapsed

    play_r2() #calls function to play Random R2 sounds
    delay = randint(1,3);
    timeElapsed += delay
    print(': play_r2_with_random_delays called with a delay of: ', delay, 'Time Elapsed: ', timeElapsed)
    timer_task = Timer(delay, play_r2_with_random_delays, ()) # Create New Timer Task
    aux_mode_timer_dict['RANDOM_R2_SOUNDS_TIMER'] = timer_task
    timer_task.start()  # Start Timer Task

def stop_r2_with_random_delays(): #turn off Random R2 sounds
    timer_task = aux_mode_timer_dict['RANDOM_R2_SOUNDS_TIMER']
    timer_task.cancel()

def play_r2():
    print('play_r2 function entered.')
    if aux_power_on:
        if not r2_channel.get_busy():
            print("not busy")
            soundwav = random.choice(r2_sound_files)
            r2d2sound1 = pygame.mixer.Sound(soundwav)
            r2_channel.play(r2d2sound1)

def play_radio_with_random_delays():
    global aux_mode_timer_dict
    global timeElapsed

    play_radio() #calls function to play Random radio sounds
    delay = randint(1,3);  # Calculate Delay
    timeElapsed += delay
    print(': play_radio_with_random_delays called with a delay of: ', delay, 'Time Elapsed: ', timeElapsed)
    timer_task = Timer(delay, play_radio_with_random_delays, ())  # Create New Timer Task
    aux_mode_timer_dict['RANDOM_radio_SOUNDS_TIMER'] = timer_task  # Start Timer Task
    timer_task.start()

def stop_radio_with_random_delays(): #turn off Random radio sounds
    timer_task = aux_mode_timer_dict['RANDOM_radio_SOUNDS_TIMER']
    timer_task.cancel()

def play_radio():
    print('play_radio function entered.')
    if aux_power_on:
        if not radio_channel.get_busy():
            print("not busy")
            soundwav = random.choice(radio_sound_files)
            radiosound1 = pygame.mixer.Sound(soundwav)
            radio_channel.play(radiosound1)

def play_yoda():
    print('play_yoda function entered.')
    if aux_power_on:
        if not yoda_channel.get_busy():
            print("not busy")
            soundwav = random.choice(yoda_sound_files)
            yodasound1 = pygame.mixer.Sound(soundwav)
            yoda_channel.play(yodasound1)
		
def start_enemy_fighters():
    print('start_enemy_fighters function entered')
    if engine_started:
        if not tie_fighter_channel.get_busy():
            print('not busy')
            tie_fighter_channel.play(alarm_sound)
            timer_task = Timer(5, play_tie_fighter_with_random_delays, ())  # Create New Timer Task
            power_mode_timer_dict['tie_fighter_alarm_TIMER'] = timer_task
            print('start timer after alarm')
            timer_task.start()  # Start Timer Task
	    
def stop_enemy_fighters():
    if tie_fighter_channel.get_busy():
        tie_fighter_channel.stop()
        timer_task = power_mode_timer_dict['tie_fighter_alarm_TIMER']
        timer_task.cancel()
    print('stop_enemy_fighters funtion')
    stop_tie_fighter_with_random_delays()

def play_tie_fighter_with_random_delays():   #Play random Tie Fighter Sounds, with Random Delays Between
    # Need this here to say that we want to modify the global copy
    global aux_mode_timer_dict
    global timeElapsed

    play_tie_fighter() #calls function to play Random tighter fighter sounds
    delay = randint(1,3);  # Calculate Delay
    timeElapsed += delay
    print(': play_tie_fighter_with_random_delays called with a delay of: ', delay, 'Time Elapsed: ', timeElapsed)
    # Create New Timer Task
    timer_task = Timer(delay, play_tie_fighter_with_random_delays, ())
    power_mode_timer_dict['RANDOM_tie_fighter_SOUNDS_TIMER'] = timer_task  
    timer_task.start() # Start Timer Task

def stop_tie_fighter_with_random_delays(): #turn off Random tie fighter sounds
    key='RANDOM_tie_fighter_SOUNDS_TIMER'
    if key in power_mode_timer_dict and power_mode_timer_dict[key]:   #make sure key exists & that it has a value ******************** ADD THIS CODE TO ALL TIMER CANCEL CODE ****
        timer_task = power_mode_timer_dict[key]
        timer_task.cancel()

def play_tie_fighter():
    print('play_tie_fighter function entered.')
    if engine_started:	
        if not tie_fighter_channel.get_busy():
            print("not busy")
            soundwav = random.choice(tie_fighter_sound_files)
            sound1 = pygame.mixer.Sound(soundwav)
            tie_fighter_channel.play(sound1)

def engage_hyperdrive():
    print('engage_hyperdrive function entered.')
    if engine_started:	
        if not hyperdrive_channel.get_busy():  
            if foil_position_closed:
                hyperdrive_channel.play(hyperdrive_sound)
            else:
                error_sound.play()

def open_foil():
    global foil_position_closed

    print('open_foil function entered.')
    if engine_started:	
        if not foil_channel.get_busy():  
            foil_channel.play(foil_sound)
    foil_position_closed = False

def close_foil():
    global foil_position_closed

    print('close_foil function entered.')
    if engine_started:	
        if not foil_channel.get_busy():  
            foil_channel.play(foil_sound)
        foil_position_closed = True

def lower_landing_gear():
    global landing_gear_down

    print('lower_landing_gear function entered.')
    if engine_started:
        landing_gear_sound.play()
    landing_gear_down = True

def raise_landing_gear():
    global landing_gear_down

    print('raise_landing_gear function entered.')
    if engine_started:
        landing_gear_sound.play()
    landing_gear_down = False

def arm_weapons():
    global weapons_armed

    print('arm_weapons function entered.')
    if engine_started:
        weapons_armed_sound.play()
    weapons_armed = True

def disarm_weapons():
    global weapons_armed

    print('disarm_weapons function entered.')
    if engine_started:
        acknowledge_sound.play()
    weapons_armed = False

def select_weapon(self):
    global weapon_selected
    
    if engine_started:    
        weapon_selected = self 
        button_press_sound.play()

def fire_weapon():
#    if (engine_started and weapons_armed):
    print('fire_weapon function entered.')
    if engine_started and weapons_armed:
        if weapon_selected == 1:
            laser1_sound.play()
        elif weapon_selected == 2:
            laser2_sound.play()
        elif weapon_selected == 3:
            laser3_sound.play()
        elif weapon_selected == 4:
            torpedo_sound.play()
    elif engine_started and not weapons_armed:
        error_sound.play()

def turn_on_microphone():
    if aux_power_on:
        print('microphone on')
        microphone_on_sound.play()

def play_alarm():
    if aux_power_on:
        print('function play alarm')
        alarm_sound.play()

def turn_off_microphone():
    if aux_power_on:
        print('microphone off')  #consider doing this on a channel so it can't repeat
        microphone_on_sound.play()

def play_chewy():
    print('play_chewy function entered.')
    if aux_power_on:
        if not chewy_channel.get_busy():
            print("not busy")
            soundwav = random.choice(chewy_sound_files)
            chewysound1 = pygame.mixer.Sound(soundwav)
            chewy_channel.play(chewysound1)

def play_hat():
    if engine_started:
        print('joystick hat button moved')
        error_sound.play()

def play_turn_sound():
    if engine_started:
        print('Xwing turning moved')
        xwing_turn_sound.play()

def print_instructions():
    # Print BEGIN PROGRAM Statement
    print('MAKE SURE LITTLE WINDOW HAS FOCUS FOR KEYBOARD KEYS ENTRY TO WORK')
    print('Press q to quit')
    print('Press k for key to unlock')
    print('Press l for key to lock')
    print('Press i for auxilary power on')
    print('Press o for auxilary power off')
    print('Press s to start engine')
    print('Press w to arm/disarm weapons')
    print('Press 1 to select  laser1')
    print('Press 2 to select laser2')
    print('Press 3 to select laser3')
    print('Press 4 to select torpedo')
    print('Press space to fire weapon')
    print('Press h for hyperdrive')
    print('Press m to toggle music')
    print('Press f to open & close foil')
    print('Press & hold r for R2 Radio')
    print('Press & hold a for Alliance Radio')
    print('Press & hold t for R2 Radio')
    print('Press F1 to hear Yoda')
    print('Press F2 to hear Chewy')
    print('Press F5 to land - gear must be down')

################################ HANDLE INPUT ############################
def read_joystick_gpio_and_keyboard():
    # HANDLE GPIO EVENTS
    if GPIO.event_detected(master_lock_gpio_pin):
        time.sleep(0.05)
        print("GPIO MasterLock:", GPIO.input(master_lock_gpio_pin))
        if GPIO.input(master_lock_gpio_pin):
            lock()
        else:
            unlock()
    if GPIO.event_detected(aux_power_gpio_pin):
        time.sleep(0.02) 
        print("GPIO Aux Power:", GPIO.input(aux_power_gpio_pin))
        if GPIO.input(aux_power_gpio_pin):
            turn_aux_power_on()
        else:
            turn_aux_power_off()
    if GPIO.event_detected(engine_start_gpio_pin):
        print("Start Button Pressed")
        start_engine()
    if GPIO.event_detected(foil_gpio_pin):
        time.sleep(0.02)
        print("GPIO Foil Event:", GPIO.input(foil_gpio_pin))
        if GPIO.input(foil_gpio_pin):
            open_foil()
        else:
            close_foil()
    if GPIO.event_detected(landing_gear_gpio_pin):
        time.sleep(0.02)
        print("GPIO Landing Gear:", GPIO.input(landing_gear_gpio_pin))
        if GPIO.input(landing_gear_gpio_pin):
            raise_landing_gear()
        else:
            lower_landing_gear()
    if GPIO.event_detected(r2_radio_gpio_pin):
        time.sleep(0.02)
        print("GPIO R2 Radio:", GPIO.input(r2_radio_gpio_pin))
        if GPIO.input(r2_radio_gpio_pin):
            play_r2_with_random_delays()
        else:
            stop_r2_with_random_delays()
    if GPIO.event_detected(alliance_radio_gpio_pin):
        time.sleep(0.02)
        print("GPIO Alliance Radio:", GPIO.input(alliance_radio_gpio_pin))
        if GPIO.input(alliance_radio_gpio_pin):
            play_radio_with_random_delays()
        else:
            stop_radio_with_random_delays()
    if GPIO.event_detected(arm_weapons_gpio_pin):
        time.sleep(0.02)
        print("GPIO Weapons Armed :", GPIO.input(arm_weapons_gpio_pin))
        if GPIO.input(arm_weapons_gpio_pin):
            arm_weapons()
        else:
            disarm_weapons()
    if GPIO.event_detected(hyperdrive_gpio_pin):
        print("Hyperdrive Button Pressed")
        engage_hyperdrive()
    if GPIO.event_detected(f1_button_gpio_pin):
        print("F1 Button Pressed")
        #Feature here
    if GPIO.event_detected(f2_button_gpio_pin):
        print("F2 Button Pressed")
        #Feature here
    if GPIO.event_detected(f3_button_gpio_pin):
        print("F3 Button Pressed")
        #Feature here
    if GPIO.event_detected(f4_button_gpio_pin):
        print("F4 Button Pressed")
        #Feature here
    if GPIO.event_detected(f5_button_gpio_pin):
        print("F5 Button Pressed")
        #Feature here
    if GPIO.event_detected(f6_button_gpio_pin):
        print("F6 Button Pressed")
        #Feature here
    if GPIO.event_detected(f7_button_gpio_pin):
        print("F7 Button Pressed")
        #Feature here
    if GPIO.event_detected(f8_button_gpio_pin):
        print("F8 Button Pressed")
        #Feature here

    # HANDLE KEYBOARD EVENTS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            led_flash_thread.kill()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            print("keyboard KEYDOWN")
            if event.key == pygame.K_s:
                print("Key s down")
                start_engine()
            if event.key == pygame.K_F1:
                print("Key F1 down")
                play_yoda()
            if event.key == pygame.K_F2:
                print("Key F2 down")
                play_chewy()
            if event.key == pygame.K_F3:
                print("Key F3 down")
                turn_on_microphone()
            if event.key == pygame.K_F4:
                print("Key F4 down")
                turn_off_microphone()
            if event.key == pygame.K_F5:
                print("Key F5 down")
                land_xwing()
            if event.key == pygame.K_F6:
                print("Key F6 down")
                error_sound.play()
            if event.key == pygame.K_F7:
                print("Key F7 down")
                landing_sound.play()
            if event.key == pygame.K_F8:
                print("Key F8 down")
                error_sound.play()
            elif event.key == pygame.K_1:
                print("Key 1 down")
                select_weapon(1)
            elif event.key == pygame.K_2:
                print("Key 2 down")
                select_weapon(2)
            elif event.key == pygame.K_3:
                print("Key 3 down")
                select_weapon(3)
            elif event.key == pygame.K_4:
                print("Key 4 down")
                select_weapon(4)
            elif event.key == pygame.K_r:
                print("Key r down")
                play_r2_with_random_delays()
            elif event.key == pygame.K_t:
                print("Key t down")
                start_enemy_fighters()
            elif event.key == pygame.K_k:
                print("Key k down")
                unlock()
            elif event.key == pygame.K_l:
                print("Key l down")
                lock()
            elif event.key == pygame.K_m:
                print("Key m down")
                toggle_music()
            elif event.key == pygame.K_i:
                print("Key i down")
                turn_aux_power_on()
            elif event.key == pygame.K_o:
                print("Key o down")
                turn_aux_power_off()
            elif event.key == pygame.K_a:
                print("Key a down")
                play_radio_with_random_delays()
            elif event.key == pygame.K_g:
                print("Key g down")
                if landing_gear_down:
                    raise_landing_gear()
                else:
                    lower_landing_gear()
            elif event.key == pygame.K_h:
                print("Key h down")
                engage_hyperdrive()
            elif event.key == pygame.K_w:
                print("Key w down")
                if weapons_armed:
                    disarm_weapons()
                else:
                    arm_weapons()
            elif event.key == pygame.K_SPACE:
                print("Key SPACE down")
                fire_weapon()
            elif event.key == pygame.K_f:
                print("Key f down")
                if foil_position_closed:
                    open_foil()
                else:
                    close_foil()
            elif event.key == pygame.K_q:
                pygame.quit()
                led_flash_thread.kill() # this causes an error on x86 because no GPIO
                sys.exit()
        if event.type == pygame.KEYUP:
            print("keyboard KEYUP")
            if event.key == pygame.K_r:
                print("Key r up")
                stop_r2_with_random_delays()
            if event.key == pygame.K_t:
                print("Key t up")
                stop_enemy_fighters()
            if event.key == pygame.K_a:
                print("Key a up")
                stop_radio_with_random_delays()
        # HANDLE JOYSTICK EVENTS
        if event.type == pygame.JOYBUTTONDOWN:
            button = event.button
            if button == 0:
                fire_weapon()
            elif button == 1:
                turn_on_microphone()
            elif button == 2:
                select_weapon(2)
            elif button == 3:
                select_weapon(3)
            elif button == 4:  # order of weapon selection button on joy not in order
                select_weapon(1)
            elif button == 5:
                select_weapon(4)
            elif button == 6:
                engage_hyperdrive()
            elif button == 7:
                fire_weapon()
            elif button == 8:
                open_foil()
            elif button == 9:
                close_foil()
            elif button == 10:
                play_radio_with_random_delays()
            elif button == 11:
                play_r2_with_random_delays()
            print("Button {} on".format(button))
        if event.type == pygame.JOYBUTTONUP:
            button = event.button
            if button == 1:
                turn_off_microphone()
            elif button == 11:
                stop_r2_with_random_delays() #turn off Random R2 sounds
            elif button == 10:
                stop_radio_with_random_delays()
            print("Button {} off".format(button))
        if event.type == pygame.JOYHATMOTION:
            if event.hat == 0:
                print("event value hat axis 0: {}".format(event.value))
                play_hat()
        if event.type == pygame.JOYAXISMOTION:
            if event.axis == 0:
                #print("event value axis 0: {}".format(event.value))
                if event.value > 0.7:
                    play_turn_sound()
                elif event.value < -0.7:
                    play_turn_sound()
            elif event.axis == 1:
                #print("event value axis 1: {}".format(event.value))
                #print("event value axis 0: {}".format(event.value))
                if event.value > 0.7:
                    play_turn_sound()
                elif event.value < -0.7:
                    play_turn_sound()
            elif event.axis == 2:
                #print("event value axis 2: {}".format(event.value))
            elif event.axis == 3:
                #print("event value axis 3: {}".format(event.value))
                set_engine_volume()
                #self.verticalPosition = event.value

################################ INITIALIZE GPIO ############################
#define GPIO Pin assignment
shared_led_power_gpio_pin=6
master_lock_gpio_pin=21
aux_power_gpio_pin=20
engine_start_gpio_pin=26
engine_start_led_gpio_pin=19
foil_gpio_pin=16
landing_gear_gpio_pin=12
hyperdrive_gpio_pin=7
arm_weapons_gpio_pin=13
#arm_weapons_led_gpio_pin=
r2_radio_gpio_pin=11
alliance_radio_gpio_pin=5
f1_button_gpio_pin= 8
f1_led_gpio_pin=25
f2_button_gpio_pin=24
f2_led_gpio_pin=23
f3_button_gpio_pin=18
f3_led_gpio_pin=15
f4_button_gpio_pin=9
f4_led_gpio_pin=10
f5_button_gpio_pin=22
f5_led_gpio_pin=27
f6_button_gpio_pin=17
f6_led_gpio_pin=4
f7_button_gpio_pin=3
f7_and_f8_led_gpio_pin=2
f8_button_gpio_pin=14
# f8_led_gpio_pin=2  Shared with f7 LED Pin

#check if running on Raspberry Pi
if os.uname()[4][:3] == 'arm':  # means running on Pi else it will equal 'x86' for Windows Laptop
    running_on_pi = True
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(shared_led_power_gpio_pin,GPIO.OUT)
    GPIO.output(shared_led_power_gpio_pin, True)
    GPIO.setup(master_lock_gpio_pin,GPIO.IN)
    GPIO.setup(aux_power_gpio_pin,GPIO.IN)
    GPIO.setup(engine_start_gpio_pin,GPIO.IN)
    GPIO.setup(engine_start_led_gpio_pin,GPIO.OUT)
    GPIO.output(engine_start_led_gpio_pin, False)

    GPIO.setup(foil_gpio_pin,GPIO.IN)
    GPIO.setup(landing_gear_gpio_pin,GPIO.IN)
    GPIO.setup(hyperdrive_gpio_pin,GPIO.IN)
    GPIO.setup(arm_weapons_gpio_pin,GPIO.IN)
    GPIO.setup(r2_radio_gpio_pin,GPIO.IN)
    GPIO.setup(alliance_radio_gpio_pin,GPIO.IN)
    GPIO.setup(f1_button_gpio_pin,GPIO.IN)
    GPIO.setup(f1_led_gpio_pin,GPIO.IN)
    GPIO.setup(f2_button_gpio_pin,GPIO.IN)
    GPIO.setup(f2_led_gpio_pin,GPIO.OUT)
    GPIO.setup(f3_button_gpio_pin,GPIO.IN)
    GPIO.setup(f3_led_gpio_pin,GPIO.OUT)
    GPIO.setup(f4_button_gpio_pin,GPIO.IN)
    GPIO.setup(f4_led_gpio_pin,GPIO.OUT)
    GPIO.setup(f5_button_gpio_pin,GPIO.IN)
    GPIO.setup(f5_led_gpio_pin,GPIO.OUT)
    GPIO.setup(f6_button_gpio_pin,GPIO.IN)
    GPIO.setup(f6_led_gpio_pin,GPIO.OUT)
    GPIO.setup(f7_button_gpio_pin,GPIO.IN)
    GPIO.setup(f7_and_f8_led_gpio_pin,GPIO.OUT)
    GPIO.setup(f8_button_gpio_pin,GPIO.IN)

    # Enable Event Handling for GPIO Input Pins - ie. switches & buttons
    GPIO.add_event_detect(master_lock_gpio_pin, GPIO.BOTH, bouncetime=400)  
    GPIO.add_event_detect(aux_power_gpio_pin, GPIO.BOTH, bouncetime=200)
    GPIO.add_event_detect(engine_start_gpio_pin, GPIO.FALLING, bouncetime=400)
    GPIO.add_event_detect(foil_gpio_pin, GPIO.BOTH, bouncetime=400)
    GPIO.add_event_detect(landing_gear_gpio_pin, GPIO.BOTH, bouncetime=400)
    GPIO.add_event_detect(hyperdrive_gpio_pin, GPIO.FALLING, bouncetime=400)
    GPIO.add_event_detect(arm_weapons_gpio_pin, GPIO.BOTH, bouncetime=400)
    GPIO.add_event_detect(r2_radio_gpio_pin, GPIO.BOTH, bouncetime=400)
    GPIO.add_event_detect(alliance_radio_gpio_pin, GPIO.BOTH, bouncetime=400)
    GPIO.add_event_detect(f1_button_gpio_pin, GPIO.FALLING, bouncetime=400)
    GPIO.add_event_detect(f2_button_gpio_pin, GPIO.FALLING, bouncetime=400)
    GPIO.add_event_detect(f3_button_gpio_pin, GPIO.FALLING, bouncetime=400)
    GPIO.add_event_detect(f4_button_gpio_pin, GPIO.FALLING, bouncetime=400)
    GPIO.add_event_detect(f5_button_gpio_pin, GPIO.FALLING, bouncetime=400)
    GPIO.add_event_detect(f6_button_gpio_pin, GPIO.FALLING, bouncetime=400)
    GPIO.add_event_detect(f7_button_gpio_pin, GPIO.FALLING, bouncetime=400)
    GPIO.add_event_detect(f8_button_gpio_pin, GPIO.FALLING, bouncetime=400)

# Get initial GPIO settings and set flags
    if GPIO.input(master_lock_gpio_pin):
        master_lock_on = True
    else:
        master_lock_on = False
    print("Master Lock value = ", master_lock_on)
    if GPIO.input(aux_power_gpio_pin):
        aux_power_on = True
    else:
        aux_power_on = False
    print("Aux Power = ", aux_power_on)
    if GPI.input(foil_gpio_pin):
        foil_position_closed = False
    else:
        foil_position_closed = True
    print ("Foil position closed = ", foil_position_closed)
    if GPI.input(landing_gear_gpio_pin):
        landing_gear_down = False
    else:
        landing_gear_down = True
    print ("Landing Gear Down = ", landing_gear_down)
    if GPI.input(arm_weapons_gpio_pin):
        weapons_armed = True
    else:
        weapons_armed = False
    print ("Weapons armed = ", foil_position_closed)
else:
    running_on_pi = False


################################ MAIN GAME LOOP ############################
gameloop = True
if __name__ == '__main__':
    global aux_mode_timer_dict      # Need this here to say that we want to modify the global copy
    print_instructions()
    while gameloop:
        read_joystick_gpio_and_keyboard()
          # Print END PROGRAM Statement
        #time.sleep(0.01) #adding this gives subprocesses like detecting GPIO time to do their thing, fixed delay when pressing GPIO button
    print('END PROGRAM')
    pygame.quit() # clean exit

