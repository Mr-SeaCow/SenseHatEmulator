from sense_emu import SenseHat
from time import sleep
sense = SenseHat()

t_str = 'Hello World!'

sense.load_image('pixil-frame-0.png')

sleep(2)
