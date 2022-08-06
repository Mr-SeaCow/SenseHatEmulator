from PIL import Image

import os
import sys
import pygame
import math
import time

from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_SPACE,
    K_ESCAPE,
    KEYUP,
    KEYDOWN,
    QUIT,
)

pygame.init()

FILE_NAME = sys.argv[0].split('/')[-1].replace('.py', '')

pygame.display.set_caption(f'SenseHat Display Emulator: {FILE_NAME}')

pygame.event.set_blocked(None)
pygame.event.set_allowed(KEYUP)
pygame.event.set_allowed(KEYDOWN)
pygame.event.set_allowed(QUIT)


sideOffset = 0

SCREEN_WIDTH = 800 + sideOffset
SCREEN_HEIGHT = 800

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

screen.fill((125, 125, 125))

KEY_LOOKUP = {K_UP: 'up',K_DOWN: 'down',K_LEFT: 'left',K_RIGHT: 'right', K_SPACE: 'middle'}
ACT_LOOKUP = {KEYDOWN: 'pressed', KEYUP: 'released'}

class StickEvent:
    def __init__(self, dir, act):
        self.direction = dir
        self.action = act
        self.time = time.time()
   
    def __str__(self):
        return f"(timestamp: {self.time}, direction: {self.direction}, action: {self.action})"

    def __repr__(self):
         return f"(timestamp: {self.time}, direction: {self.direction}, action: {self.action})"

class Stick:
    def __init__(self):
        self._events = []

    def get_events(self):
        for event in pygame.event.get():
            if (event.type == KEYDOWN or event.type == KEYUP) and event.key in [K_UP,K_DOWN,K_LEFT,K_RIGHT, K_SPACE]:
                self._events.append(StickEvent(KEY_LOOKUP[event.key], ACT_LOOKUP[event.type]))

            elif event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                exit()
    
        tempCopy = self._events.copy()
        
        self._events = []

        return tempCopy

class SenseHat:
    def __init__(self, text_assets='sense_hat_text'):
        self._pixels = []
        self._rotation = 0
        self._stick = Stick()

        self._pixel_block_offset = (screen.get_width() / 8)
        self._pixel_block_size = self._pixel_block_offset * 0.9
        self._pixel_block_spacing = self._pixel_block_offset * .05

        for _ in range(64):
            self._pixels.append((0, 0, 0))

        self._set_pixels()

        dir_path = os.path.dirname(__file__)
        self._load_text(
            os.path.join(dir_path, f"{text_assets}.png"),
            os.path.join(dir_path, f"{text_assets}.txt")
        )

    @property
    def stick(self):
        return self._stick

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, r):
        self.set_rotation(r, True)

    def get_pixel(self, x, y):
        if self._coords_are_valid(x, y) == False:
            raise Exception(f"Coords provided are out of bounds: ({x} {y})")

        u_coords = self._convert_to_unary(x, y)

        return self._pixels[u_coords]

    def get_pixels(self):
        return self._pixels

    def set_pixel(self, x, y, *args):

        if self._coords_are_valid(x, y) == False:
            raise Exception(f"Coords provided are out of bounds: ({x} {y})")

        color_val = self._unpack_rgb(*args)

        self._validate_rgb(color_val)

        u_coords = self._convert_to_unary(x, y)

        self._pixels[u_coords] = color_val

        self._set_pixel(x, y, color_val)

        return

    def set_pixels(self, pixel_ara):

        if len(pixel_ara) != 64:
            raise Exception("Pixel List must be of length 64.")
        
        for pixel in pixel_ara:
            self._validate_rgb(pixel)

        self._pixels = pixel_ara

        self._set_pixels()

        return

    def set_rotation(self, rot=0, redraw=True):
        if not isinstance(rot, int) or rot < 0 or rot > 270 or rot % 90 != 0:
            raise ValueError('Rotation must be an integer value of (0, 90, 180, 270)')

        self._rotation = rot

        if redraw:
            self._set_pixels()

        return None

    def show_letter(self, letter, text_colour=[255, 255, 255], back_colour=[0, 0, 0]):
        
        if len(letter) > 1:
            raise ValueError('Only one character may be passed to this method.')

        dummy_color = back_colour
        pixel_list = [dummy_color] * 8
        pixel_list.extend(self._get_char_pixels(letter))
        pixel_list.extend([dummy_color] * 16)
        colored_pixels = [
            text_colour if pixel == [255, 255, 255] else back_colour
            for pixel in pixel_list
        ]
        colored_pixels = self._rotate_pixels_CCW(colored_pixels, back_colour)
        self.set_pixels(colored_pixels)

    def show_message(self, text, scroll_speed=.1, text_colour=[255, 255, 255], back_colour=[0, 0, 0]):
       
        dummy_color = back_colour
        string_padding = [dummy_color] * 64
        letter_padding = [dummy_color] * 8

        scroll_pixels = []
        scroll_pixels.extend(string_padding)

        for s in text:
            scroll_pixels.extend(self._trim_whitespace(self._get_char_pixels(s)))
            scroll_pixels.extend(letter_padding)

        scroll_pixels.extend(string_padding)

        colored_pixels = [
            text_colour if pixel == [255, 255, 255] else back_colour
            for pixel in scroll_pixels
        ]

        scroll_length = len(colored_pixels) // 8
        for i in range(scroll_length - 8):
            start = i * 8
            end = start + 64
            self.set_pixels(self._rotate_pixels_CCW(colored_pixels[start:end], back_colour))
            time.sleep(scroll_speed)

    def clear(self, *args):
        if len(args) == 0:
            self._fill_pixels((0, 0, 0))
            self._set_pixels()
            return

        color_val = self._unpack_rgb(*args) # POTENTIAL ERROR

        self._validate_rgb(color_val)

        self._fill_pixels(color_val)
        
        self._set_pixels()

        return

    def load_image(self, file_path, redraw=True):

        if not os.path.exists(file_path):
            raise IOError(f"{file_path} is not found")

        img = Image.open(file_path).convert('RGB')
        img_pixels = list(map(list, img.getdata()))

        if redraw:
            self.set_pixels(img_pixels)   

        return img_pixels 

    def flip_h(self, redraw=True):
        pixel_list = self.get_pixels()
        flipped_list = []

        for i in range(8):
            offset = i * 8
            flipped_list.extend(reversed(pixel_list[offset:offset + 8]))
    
        if redraw:
            self.set_pixels(flipped_list)

        return flipped_list

    def flip_v(self, redraw=True):
        pixel_list = self.get_pixels()
        flipped_list = []

        for i in reversed(range(8)):
            offset = i * 8
            flipped_list.extend(pixel_list[offset:offset + 8])
        
        if redraw:
            self.set_pixels(flipped_list)

        return flipped_list

    def _convert_from_unary(self, u):

        if u < 0 or u >= 64:
            raise Exception(f"Unary value must be between 0-63")

        x = u % 8
        y = math.floor((u - x) / 8)

        return (x, y)
            
    def _convert_to_unary(self, x, y):
        if self._coords_are_valid(x, y) == False:
            raise Exception(f"Coords provided are out of bounds: ({x} {y})")

        temp_num = x
        temp_num += y * 8

        return temp_num
        
    def _coords_are_valid(self, x, y):
        return 0 <= x <= 7 and 0 <= y <= 7

    def _get_char_pixels(self, c):
        if len(c) == 1 and c in self._text_dict.keys():
            return list(self._text_dict[c])
        else:
            return list(self._text_dict['?'])

    def _load_text(self, img_file, txt_file):
        
        img_pixels = self.load_image(img_file, False)

        with open(txt_file, 'r') as f:
            loaded_txt = f.read()

        self._text_dict = {}

        for idx, s in enumerate(loaded_txt):
            start = idx * 40
            end = start + 40
            char = img_pixels[start:end]
            self._text_dict[s] = char

    def _fill_pixels(self, color):

        self._validate_rgb(color)

        self._pixels = []

        for _ in range(64):
            self._pixels.append(color)

        return

    def _flatten_ara(self, ara):
        if len(ara) == 0:
            return ara
        
        if len(ara[0]) == 0:
            return ara

        flat_ara = []

        for i in range(len(ara)):
            for val in ara[i]:
                flat_ara.append(val)

        return flat_ara

    def _rotate_pixels_CW(self, matrix, back_color=[0, 0, 0]):
        size = int(math.sqrt(len(matrix)))
        result = [back_color] * 64
        
        for i in range(size):
            for j in range(size):
                result[i * size + j] = matrix[(size - j - 1) * size + i]


        return result 

    def _rotate_pixels_CCW(self, matrix, back_color=[0, 0, 0]):
        size = int(math.sqrt(len(matrix)))
        result = [back_color] * 64
        
        for i in range(size):
            for j in range(size):
                result[(size - j - 1) * size + i] = matrix[i * size + j]


        return result 

    def _rotate_pixels(self, pixels):
        if self._rotation == 90:
            return self._rotate_pixels_CW(pixels)
        elif self._rotation == 180:
            return self._rotate_pixels_CW(self._rotate_pixels_CW(pixels))
        elif self._rotation == 270:
            return self._rotate_pixels_CCW(self._rotate_pixels_CCW(pixels))
        
        return pixels

    def _set_pixel(self, x, y, color_val):

        rect = pygame.Rect(
            x*self._pixel_block_offset+self._pixel_block_spacing,
            y*self._pixel_block_offset+self._pixel_block_spacing,
            self._pixel_block_size,
            self._pixel_block_size
            )
        pygame.draw.rect(screen, color_val, rect)

        pygame.display.update()

        return

    def _set_pixels(self):
        pixels = self._rotate_pixels(self._pixels.copy())
        for i in range(len(pixels)):
            x,y = self._convert_from_unary(i)

            rect = pygame.Rect(
                x*self._pixel_block_offset+self._pixel_block_spacing,
                y*self._pixel_block_offset+self._pixel_block_spacing,
                self._pixel_block_size,
                self._pixel_block_size
                )

            pygame.draw.rect(screen, pixels[i], rect)

        pygame.display.update()

    def _trim_whitespace(self, char):
        psum = lambda x: sum(sum(x, []))
        if psum(char) > 0:
            is_empty = True
            while is_empty:
                row = char[0:8]
                is_empty = psum(row) == 0
                if is_empty:
                    del char[0:8]
            is_empty = True
            while is_empty:
                row = char[-8:]
                is_empty = psum(row) == 0
                if is_empty:
                    del char[-8:]
        return char

    def _unpack_rgb(self, *args):
        if len(args) == 1:
            args = args[0]

        return args

    def _validate_rgb(self, color):
        if len(color) != 3:
            raise Exception(f"Invalid RGB array {color}")
        
        for c in color:
            if (0 <= c <= 255) == False or isinstance(c, int) == False:
                raise Exception(f"Invalid RGB values {color}")
        
        return True
