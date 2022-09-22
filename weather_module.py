#!/usr/bin/python3

#Libraries
import Adafruit_DHT as dht
from time import sleep
import RPi.GPIO as GPIO
import time
import colorsys
import os
from PIL import Image, ImageDraw, ImageFont
import argparse
import netifaces as ni
from gpiozero import InputDevice

########################################################

# Parse the command arguments
parser = argparse.ArgumentParser(prog='weather_module', description='Weather module with OLED display')
parser.add_argument('--OLED', help='Add if OLED screen is installed', action='store_true', default=False)
parser.add_argument('--interface', type=str, default="eth0")

args = parser.parse_args()
OLED_SCREEN_INSTALLED = args.OLED
INTERFACE = args.interface

if OLED_SCREEN_INSTALLED:
    import adafruit_ssd1306
    from board import SCL, SDA
    import busio

    i2c = busio.I2C(SCL, SDA) # Initialize the I2C bus for the OLED screen

    oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c) # Initialize OLED screen (128x64 pixels)
    oled.fill(0) # Fill the screen with 0's (clear screen)

########################################################

GPIO.setmode(GPIO.BCM) # Use processor pin numbering system  

########################################################

DHT_PIN = 4 # Set DATA pin
RAIN_SENSOR_PIN = 18

########################################################


def read_temperature_and_humidity():
    #Read Temp and Hum from DHT22
    h,t = dht.read_retry(dht.DHT22, DHT_PIN)
    temperature_C = '{0:0.1f}*C'.format(t)
    humidity = '{0:0.1f}%'.format(h)
    return temperature_C, humidity

def get_rain_status():
    rain = InputDevice(RAIN_SENSOR_PIN)
    if rain.is_active:
        return "It's raining."
    else:
        return "It is not raining."

    
def get_ip_addr():
    ip = ni.ifaddresses(INTERFACE)[ni.AF_INET][0]['addr']
    return ip


if OLED_SCREEN_INSTALLED:
    # Show Raspberry Pi Logo on OLED screen for 1 sec
    image = Image.open("RPI.bmp") 
    oled.image(image)
    oled.show()
    sleep(1)
    ##################################################

    oled.fill(0) # fill the screen with 0's (clear screen)


    
    while True:
        # Open a new blank image and draw object to later draw tex and shapes on
        image = Image.new("1", (oled.width, oled.height))
        draw = ImageDraw.Draw(image)
        #########################################################################
        oled.fill(0) # fill the screen with 0's (clear screen)

        # Load a font in 2 different sizes.
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
        font2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)

        # Draw the text that doesn't need updating
        draw.text((0, 0), "IP address: "+get_ip_addr(), font=font, fill=255, align="right")
        draw.line((0, 12, 127, 12), width=1, fill=255) # draw horizontal seperation line

        results = read_temperature_and_humidity()
        rain_status = get_rain_status()
        draw.text((0, 14), " Temperature: "+ results[0], font=font, fill=255, align="right")
        draw.line((0, 26, 127, 26), width=1, fill=255) # draw horizontal seperation line
        draw.text((0, 28), "Humidity: "+ results[1], font=font, fill=255, align="right")
        draw.line((0, 40, 127, 40), width=1, fill=255) # draw horizontal seperation line
        draw.text((0, 42), rain_status, font=font, fill=255, align="right")

        ##################################################################

        # Update image on OLED
        oled.image(image)
        oled.show()
        ######################
        sleep(5) #Wait 5 seconds and read again

else:
    while True:
        result = read_temperature_and_humidity()
        rain_status = get_rain_status()
        #Print Temperature and Humidity on Shell window
        print('Temp={}*C  Humidity={}%  {}'.format(result[0],result[1], rain_status))
        sleep(5) #Wait 5 seconds and read again


GPIO.cleanup() 