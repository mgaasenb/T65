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
from random import randint
from threading import Timer

# Initiate Global Flags & States
timerDict = dict() #these are global same level as import
timeElapsed = 0 #used for random delays
key_on = False
main_power_on = False
engine_started = False
weapon_selected = 1
foil_position_closed = True

# get initial GPIO settings and set States for switches, key, power, armed, radios 


# Initiate display window, required to collect key board input
game_display = pygame.display.set_mode((800, 600))
#xwing_image = pygame.image.load('xwing.png')
pygame.display.set_caption('T-65 Simulator')
game_display.fill((0,0,0)) 
#sys_font = pygame.font.SysFont("monospace",30)  #need a font file
#game_display.blit(xwing_image,(350,300))

# initiate sound mixer
pygame.mixer.pre_init(44100, -16, 2, 2048) # setup mixer to avoid sound lag (try reducing/increasing last number default is 3072)
#pygame.mixer.pre_init(44100, -16, 2, 64) # testing even smaller buffer

pygame.mixer.init()
pygame.init()                              #initialize pygame


# Initiate the Joystick
stick = pygame.joystick.Joystick(0)
stick.init()
print("initialized:",bool(stick.get_init()))
print(stick.get_name())
print("initialized:",bool(stick.get_init()))
print(stick.get_name())

# if using python2, the get_input command needs to act like raw_input:
if sys.version_info[:2] <= (2, 7):
    get_input = raw_input
else:
    get_input = input # python3


# load individual sounds files

# pygame.mixer.music.load('sounds/music.wav')  #music, update to select from all music files*****

engine_sound = pygame.mixer.Sound('sounds/engine.wav')
laser1_sound = pygame.mixer.Sound('sounds/laser1.wav')
laser2_sound = pygame.mixer.Sound('sounds/laser2.wav')
laser3_sound = pygame.mixer.Sound('sounds/laser3.wav')
torpedo_sound = pygame.mixer.Sound('sounds/torpedo.wav')  #UPDATE WITH better TORPEDO SOUND FILE!!!!*****
button_press_sound = pygame.mixer.Sound('sounds/button_press.wav')  # good sound but make it a bit quieter
button_press_sound.set_volume(.2) 
error_sound = pygame.mixer.Sound('sounds/error.wav')  
microphone_on_sound = pygame.mixer.Sound('sounds/mic_static.wav')  #UPDATE WITH Microphone static SOUND FILE!!!!*****
hyperdrive_sound = pygame.mixer.Sound('sounds/hyperdrive.wav')  
start_engine_sound = pygame.mixer.Sound('sounds/startengine.wav') 
xwing_turn_sound = pygame.mixer.Sound('sounds/xwing_turn.wav') 
xwing_turn_sound.set_volume(.3)

#failed_start_engine_sound = # Add randomly failed starts!
foil_sound = pygame.mixer.Sound('sounds/foil.wav')  #UPDATE WITH BETTER FOIL SOUND or make louder ???*****

# load groups of sound files
r2_sound_files = glob.glob("sounds/r2d2_*.wav")
radio_sound_files = glob.glob("sounds/radio_*.wav")
yoda_sound_files = glob.glob("sounds/yoda_*.wav")


#Configure Channels for Sound that can't overlap, share some of the same channels, if no chance of overlap
#************* FIX - come back and reserve these channels using pygame.mixer.set_reserved
pygame.mixer.set_num_channels(12) # default is 8
engine_channel = pygame.mixer.Channel(1) 
pygame.mixer.set_reserved(1)
r2_channel = pygame.mixer.Channel(2) 
radio_channel = pygame.mixer.Channel(3)
hyperdrive_channel = pygame.mixer.Channel(4) 
start_engine_channel = pygame.mixer.Channel(5) 
foil_channel = pygame.mixer.Channel(6) 

#def turn_on_main_power():
#    global main_power_on
#    
#    if key_on: 
#	main_power_on


def start_engine():
    global engine_started
#    global stick

    if not engine_started:	
	if not start_engine_channel.get_busy():
	    start_engine_channel.play(start_engine_sound, maxtime=4500)
	engine_started = True
	#while start_engine_channel.get_busy(): #wait until engine start sound is complete
	#    do_nothing = True
	# Play music non-stop

## NEED TO FIX TO HANDLE SCENARIO WHERE JOYSTICK NOT CONNECTED 
#	pygame.event.pump()
#	throttle_position = stick.get_axis(3)  # get the current position of an axis
#	print ('this is the throttle position')
#	print (throttle_position)
#	print ("throttle setting".format(throttle_position))
	##convert the throttle that goes from +1 to 1 (in reverse), so that it goes from 25% to 100% or set volume expect 0-1 so .5-1
	


	
#	engine_volume = ((1+(-1 * throttle_position)) * .5)
#	print ("setting volume initially to ".format(engine_volume))
#	print ("setting volume initially to ".format(engine_volume))
#	engine_sound.set_volume(engine_volume)
	engine_sound.set_volume(.25)  # USE THIS SETTING IF NO THROTTLE JOY STICK BUT NOT IF GETTING AXIS VALUE FROM JOYSTICK
	engine_sound.play(-1, fade_ms=7000)  # -1 parameter makes it loop non-stop

# initialize music & volume - need to preload with all music
#	pygame.mixer.music.set_volume(.25)
#	pygame.mixer.music.play(-1, fade_ms=9000)  # -1 parameter makes it loop non-stop



def play_r2_with_random_delays():   #Play random R2 Sounds, with Random Delays Between
	
    # Need this here to say that we want to modify the global copy
    global timerDict
    global timeElapsed
    global engine_started

    play_r2() #calls function to play Random R2 sounds
    # Calculate Delay
    delay = randint(1,3);
    timeElapsed += delay
    print(': play_r2_with_random_delays called with a delay of: ', delay, 'Time Elapsed: ', timeElapsed)

    # Create New Timer Task
    timerTask = Timer(delay, play_r2_with_random_delays, ())
    timerDict['RANDOM_R2_SOUNDS_TIMER'] = timerTask  #name of timer instance (could r2RandomSounds)

    # Start Timer Task
    timerTask.start()

def stop_r2_with_random_delays(): #turn off Random R2 sounds
    timerTask = timerDict['RANDOM_R2_SOUNDS_TIMER']  # use this & next line on button UP/Off cancel reference the right timerDict for the timer you are using...
    timerTask.cancel()

def play_r2():
    print('play_r2 function entered.')
    if engine_started:	
	if not r2_channel.get_busy():  
            print("not busy")  
            soundwav = random.choice(r2_sound_files)	
            r2d2sound1 = pygame.mixer.Sound(soundwav)
            r2_channel.play(r2d2sound1)

def play_radio_with_random_delays():   #Play random radio Sounds, with Random Delays Between
	
    # Need this here to say that we want to modify the global copy
    global timerDict
    global timeElapsed
    global engine_started

    play_radio() #calls function to play Random radio sounds
    # Calculate Delay
    delay = randint(1,3);
    timeElapsed += delay
    print(': play_radio_with_random_delays called with a delay of: ', delay, 'Time Elapsed: ', timeElapsed)

    # Create New Timer Task
    timerTask = Timer(delay, play_radio_with_random_delays, ())
    timerDict['RANDOM_radio_SOUNDS_TIMER'] = timerTask  #name of timer instance (could radioRandomSounds)

    # Start Timer Task
    timerTask.start()

def stop_radio_with_random_delays(): #turn off Random radio sounds
    timerTask = timerDict['RANDOM_radio_SOUNDS_TIMER']  # use this & next line on button UP/Off cancel reference the right timerDict for the timer you are using...
    timerTask.cancel()

def play_radio():
    print('play_radio function entered.')
    if engine_started:	
	if not radio_channel.get_busy():  
            print("not busy")  
            soundwav = random.choice(radio_sound_files)	
            radiosound1 = pygame.mixer.Sound(soundwav)
            radio_channel.play(radiosound1)

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

def select_weapon(self):
    global weapon_selected
    
    if engine_started:    
        weapon_selected = self 
	button_press_sound.play()

      
def fire_weapon():
#    if (engine_started and weapons_armed): #example of checking two flags! Remember to add Global weapons_armed
    if engine_started:
        print('fire_weapon function entered.')
	if weapon_selected == 1:
            laser1_sound.play()
	elif weapon_selected == 2:
	    laser2_sound.play()
	elif weapon_selected == 3:
	    laser3_sound.play()
	elif weapon_selected == 4:
	    torpedo_sound.play()

def turn_on_microphone():
    if engine_started:
	print('microphone on')
	microphone_on_sound.play()
	
def turn_off_microphone():
    if engine_started:
	print('microphone off')  #consider doing this on a channel so it can't repeat
	#consider adding static sound before R2 replies... may need to wait till sound is done to play R2
	microphone_on_sound.play()
	play_r2()

def play_hat():
    if engine_started:
	print('joystick hat button moved')
	error_sound.play()

def play_turn_sound():
    if engine_started:
	print('Xwing turning moved')
	xwing_turn_sound.play()


def read_joystick_and_keyboard():
    #print("reading joystick")
    for event in pygame.event.get():
	if event.type == pygame.QUIT:
  	    sys.exit()          
	#print (event.type)	
	if event.type == pygame.KEYDOWN:
	    print("keyboard KEYDOWN")
  	    if event.key == pygame.K_s:
                print("Key s down")
		start_engine()		
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
  	    elif event.key == pygame.K_h:
                print("Key h down")
		engage_hyperdrive()
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
		sys.exit()
	if event.type == pygame.KEYUP:
	    print("keyboard KEYUP")
	    if event.key == pygame.K_r:
         	print("Key r up")
		stop_r2_with_random_delays() 
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
    		play_r2_with_random_delays()  #on button ON call random music function
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
                print("event value axis 0: {}".format(event.value))
 		axis_value = event.value
		if event.value > 0.7:
		    play_turn_sound()
		elif event.value < -0.7:
		    play_turn_sound()
            elif event.axis == 1:
                print("event value axis 1: {}".format(event.value))
                print("event value axis 0: {}".format(event.value))
 		axis_value = event.value
		if event.value > 0.7:
		    play_turn_sound()
		elif event.value < -0.7:
		    play_turn_sound()
            elif event.axis == 2:
                print("event value axis 2: {}".format(event.value))
            elif event.axis == 3:
		print("event value axis 3: {}".format(event.value))
		#convert the throttle that goes from +1 to 1 (in reverse), so that it goes from 25% to 100% or set volume expect 0-1 so .5-1
		engine_volume = ((1+(-1 * event.value)) * .5)
		pygame.mixer.music.set_volume(engine_volume)
		#engine_volume = event.value
		print(engine_volume)
               # self.verticalPosition = event.value

## game loop
gameloop = True
if __name__ == '__main__':
    # Need this here to say that we want to modify the global copy
    global timerDict

    # Print BEGIN PROGRAM Statement
    print('MAKE SURE LITTLE WINDOW HAS FOCUS FOR KEYBOARD KEYS ENTRY TO WORK')
    print('Press q to quit')
    print('Press s to start engine')
    print('Press 1 to select  laser1')
    print('Press 2 to select laser2')
    print('Press 3 to select laser3')
    print('Press 4 to select torpedo')
    print('Press space to fire weapon')
    print('Press h for hyperdrive')
    print('Press f to open & close foil')
    print('Press & hold r for R2 Radio')
    while gameloop:
	read_joystick_and_keyboard()
	#read_gpio()
  
    # Print END PROGRAM Statement
    print('END PROGRAM')
    pygame.quit() # clean exit 
