import numpy as np
from PIL import Image, ImageDraw, ImageFont, FontFile
import os

MAX_LETTER_HEIGHT = 5
MAX_LETTER_WIDTH = 5

ALPHABET_3 = {
    "A": [2, 5, 7, 5, 5],
    "B": [7, 5, 6, 5, 7],
    "C": [7, 4, 4, 4, 7],
    "D": [6, 5, 5, 5, 6],
    "E": [7, 4, 7, 4, 7],
    "F": [7, 4, 7, 4, 4],
    "G": [7, 4, 7, 5 ,7],
    "H": [5 ,5, 7, 5, 5],
    "I": [7, 2, 2, 2, 7],
    "J": [1, 1, 1, 5, 7],
    "K": [5, 6, 4, 6, 5],
    "L": [4 ,4, 4, 4, 7],
    "M": [5, 7, 5, 5, 5],
    "N": [1, 5, 7, 5, 4],
    "O": [7, 5, 5, 5, 7],
    "P": [7, 5, 7, 4, 4],
    "Q": [7, 5, 7, 2, 3],
    "R": [7, 5, 7, 6, 5],
    "S": [7, 4, 7, 1, 7],
    "T": [7, 2, 2, 2, 2],
    "U": [5, 5, 5, 5, 7],
    "V": [5, 5, 5, 5, 2],
    "W": [5, 5, 5, 7, 5],
    "X": [5, 5, 2, 5, 5],
    "Y": [5, 5, 7, 2, 2],
    "Z": [7, 1, 2, 4, 7],
    " ": [0, 0, 0, 0, 0],
    ".": [0, 0, 0, 0, 1],
    "1": [1, 1, 1, 1, 1],
    "0": [2, 5, 5, 5, 2]
}

ALPHABET_5 = {
    "A": [14, 17, 31, 17, 17],
    "B": [30, 17, 30, 17, 30],
    "C": [14, 17, 16, 17, 14],
    "D": [30, 17, 17, 17, 30],
    "E": [31, 16, 28, 16, 31],
    "F": [31, 16, 28, 16, 16],
    "G": [14, 17, 16, 19, 14],
    "H": [17, 17, 31, 17, 17],
    "I": [31, 4, 4, 4, 31],
    "J": [1, 1, 1, 17, 14],
    "K": [17, 18, 28, 18, 17],
    "L": [16, 16, 16, 16, 31],
    "M": [17, 27, 21, 17, 17],
    "N": [17, 25, 21, 19, 17],
    "O": [14, 17, 17, 17, 14],
    "P": [30, 17, 30, 16, 16],
    "Q": [14, 17, 17, 21, 14],
    "R": [30, 17, 30, 18, 17],
    "S": [15, 16, 14, 1, 30],
    "T": [31, 4, 4, 4, 4],
    "U": [17, 17, 17, 17, 14],
    "V": [17, 17, 10, 10, 4],
    "W": [17, 17, 21, 21, 10],
    "X": [17, 10, 4, 10, 17],
    "Y": [17, 10, 4, 4, 4],
    "Z": [31, 2, 4, 8, 31],
    " ": [0, 0, 0, 0, 0],
    ".": [0, 0, 0, 0, 1],
    "1": [4, 4, 4, 4, 4],
    "0": [14, 17, 17, 17, 14]
}

ALPHABET_11 = {
    "0": [28, 34, 65, 65, 65, 65, 65, 65, 65, 34, 28],
    "1": [8, 24, 40, 72, 8, 8, 8, 8, 8, 8, 127],
    "2": [28, 34, 65, 65, 2, 4, 8, 16, 32, 64, 127],
    "3": [28, 34, 65, 1, 2, 14, 2, 1, 65, 34, 28],
    "4": [2, 6, 10, 18, 34, 66, 127, 2, 2, 2, 2],
    "5": [127, 64, 64, 64, 124, 2, 1, 1, 65, 65, 62],
    "6": [28, 34, 65, 64, 64, 92, 98, 65, 65, 34, 28],
    "7": [126, 65, 65, 1, 2, 4, 8, 16, 32, 64, 64],
    "8": [28, 34, 65, 65, 34, 28, 34, 65, 65, 34, 28],
    "9": [28, 34, 65, 65, 65, 63, 1, 1, 65, 34, 28],
    " ": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
}

class Letter(object):
    def __init__(self, rows:np.array):
        self.width = self.get_width(rows)
        self.height = self.get_height(rows)
        self.matrix = self.create_matrix(rows)

    def create_matrix(self, rows):
        binary_matrix = np.zeros((self.height, self.width), dtype=np.uint16)
        for i, num in enumerate(rows):
            binary_str = np.binary_repr(num)
            binary_array = np.fromiter(binary_str, np.uint16)      # reverse the order of the binary array
            binary_matrix[i, -len(binary_array):] = binary_array  # pad zeros to the left of the binary array

        return binary_matrix

    def get_width(self, rows):
        width = len(np.binary_repr(max(rows)))
        return width

    def get_height(self, rows):
        height = len(rows)
        return height

def string_to_matrix(string:str, alphabet:dict) -> np.matrix:
    spaced_string = " ".join(string.upper())
    matrix = np.hstack([Letter(alphabet[letter]).matrix for letter in list(spaced_string)])
    return matrix

def convert_char_to_bitmap(char:str, font_name: str, font_size:int, matrix_size:int, ones:bool) -> np.matrix:
    # 11x11 matrix that we'll fit the converted character into
    matrix = np.full((matrix_size, matrix_size), not ones, dtype=np.uint16)

    # create an image with the font character
    font = ImageFont.truetype(f"/usr/share/fonts/treuetype/msttcorefonts/{font_name}.ttf", font_size)
    image = Image.new('L', (font_size, font_size), color=0)
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), char, font=font, fill=255)
    # convert the image to a numpy array
    img_array = np.array(image)
    # threshold the image to create a binary image with 1s and 0s
    threshold = 127
    # this is of size "font_size"
    binary_array = np.where(img_array > threshold, ones, not ones)

    matrix[:,2:9] = binary_array[3:14, 1:8] 
    return matrix

def center_matrix(matrix_to_center, target_shape):
    matrix_to_center_shape = matrix_to_center.shape
    assert len(matrix_to_center_shape) == len(target_shape), "Input and target shapes should have the same number of dimensions"
    
    center_row = int((target_shape[0] - matrix_to_center_shape[0]) / 2)
    center_col = int((target_shape[1] - matrix_to_center_shape[1]) / 2)
    
    padding_top = center_row
    padding_bottom = target_shape[0] - matrix_to_center_shape[0] - center_row
    padding_left = center_col
    padding_right = target_shape[1] - matrix_to_center_shape[1] - center_col
    
    padding_args = [(padding_top, padding_bottom), (padding_left, padding_right)]
    for i in range(len(matrix_to_center_shape) - 2):
        padding_args.append((0, 0))

    padded_matrix = np.pad(matrix_to_center, padding_args, mode='constant', constant_values=0)
    return padded_matrix

