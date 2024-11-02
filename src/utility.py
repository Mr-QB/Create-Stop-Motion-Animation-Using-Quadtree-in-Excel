import numpy as np
import cv2
from PIL import Image, ImageDraw
from .param import *
import pickle
import concurrent.futures
import os
from openpyxl import load_workbook


def averageColour(image):
    """
    Calculate the average color of an image.

    Args:
        image (PIL.Image): Input image to calculate the average color.

    Returns:
        tuple: Average color of the image in the format (R, G, B).
    """
    image_arr = np.asarray(image)
    avg_color = np.mean(image_arr.reshape(-1, image_arr.shape[2]), axis=0)
    return (int(avg_color[0]), int(avg_color[1]), int(avg_color[2]))


def weightedAverage(hist):
    """
    Calculate the weighted average and standard deviation from a histogram.

    Args:
        hist (list): Histogram of an image, representing the count of pixels for each color level.

    Returns:
        float: Standard deviation (error) of the weighted average.
    """
    total = sum(hist)
    error = value = 0
    if total > 0:
        # Calculate the weighted average of the histogram.
        value = sum(i * x for i, x in enumerate(hist)) / total
        # Calculate the standard deviation using the weighted average to measure dispersion.
        error = sum(x * (value - i) ** 2 for i, x in enumerate(hist)) / total
        error = error**0.5  # Take the square root to obtain the standard deviation.
    return error


def getDetail(hist):
    """
    Compute the detail level of the image based on its histogram.

    Args:
        hist (list): Histogram of the image, containing brightness information for color channels.

    Returns:
        float: Intensity of detail calculated as a weighted sum of detail measures from each color channel.
    """
    red_detail = weightedAverage(hist[:256])
    green_detail = weightedAverage(hist[256:512])
    blue_detail = weightedAverage(hist[512:768])
    # Combine the detail levels of the color channels using their perceived brightness weights.
    detail_intensity = (
        red_detail * 0.2989 + green_detail * 0.5870 + blue_detail * 0.1140
    )
    return detail_intensity


def extractFrames(video_path):
    """
    Extract frames from a video file and convert them to PIL images.

    Args:
        video_path (str): The path to the video file from which frames will be extracted.

    Returns:
        list: A list of PIL images representing the extracted frames.
    """
    video_capture = cv2.VideoCapture(video_path)
    frames = []  # Initialize a list to store the extracted frames.

    fps = video_capture.get(
        cv2.CAP_PROP_FPS
    )  # Get the frames per second (FPS) of the video.

    frame_count = 0
    while True:
        success, frame = video_capture.read()
        if not success:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(frame_rgb)
        frames.append(pil_image)

        frame_count += 1

    video_capture.release()
    return frames  # Return the list of extracted frames.


def createVideoFromFrames(frames, output_path, fps=30):
    """
    Create a video file from a list of frames.

    Args:
        frames (list): A list of PIL images to be combined into a video.
        output_path (str): The path where the output video will be saved.
        fps (int): The frames per second for the output video. Default is 30.
    """
    width, height = frames[0].size

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    for frame in frames:
        frame_np = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)

        video_writer.write(frame_np)

    video_writer.release()


def getPixelColors(image):
    """
    Retrieve the color values of each pixel in an image.

    Args:
        image (PIL.Image): The image from which to extract pixel colors.

    Returns:
        list: A list of tuples, each containing the (x, y) coordinates and the
              hexadecimal color value of the corresponding pixel. The format is
              [(x1, y1, hex_color1), (x2, y2, hex_color2), ...].
    """
    width, _ = image.size

    pixel_data = list(image.getdata())

    pixel_colors = []

    for index, (r, g, b) in enumerate(pixel_data):
        x = index % width
        y = index // width
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        pixel_colors.append((x, y, hex_color))

    return pixel_colors


def adjustImageSize(image, width=None, height=None):
    """
    Resize an image while maintaining its aspect ratio.

    This function resizes an input image to a specified width or height while
    maintaining the original aspect ratio. If both width and height are None,
    the original image is returned without changes.

    Args:
        image (PIL.Image.Image): The image to be resized.
        width (int, optional): The desired width of the resized image. If None,
                               the height is used to calculate the new dimensions.
        height (int, optional): The desired height of the resized image. If None,
                                the width is used to calculate the new dimensions.

    Returns:
        PIL.Image.Image: The resized image.
    """
    if width is None and height is None:
        return image

    (original_width, original_height) = image.size

    if width is None:
        ratio = height / float(original_height)
        new_dimensions = (int(original_width * ratio), height)
    else:
        ratio = width / float(original_width)
        new_dimensions = (width, int(original_height * ratio))

    resized_image = image.resize(new_dimensions, Image.LANCZOS)

    return resized_image


def rgbToHex(rgb):
    """
    Convert an RGB color to a hexadecimal color integer.

    Args:
        rgb (tuple): A tuple representing the RGB color as (R, G, B),
                     where each value is an integer between 0 and 255.

    Returns:
        int: A hexadecimal color integer representation.
    """
    r, g, b = rgb
    return f"#{r:02x}{g:02x}{b:02x}"


def processQuadtree(quadtree):
    """
    Process a quadtree to extract pixel data and convert it to a format suitable for Excel.

    This function creates an image from the given quadtree with a custom depth and optional
    lines displayed. It iterates over each pixel to extract RGB color information and
    converts it to a hexadecimal color format.

    Args:
        quadtree (QuadTree): An instance of a QuadTree object containing hierarchical image data.

    Returns:
        list: A list of tuples where each tuple contains:
              - (x, y) (tuple): The coordinates of the pixel in the image.
              - color (str): The color of the pixel in hexadecimal format.
    """
    pixel_data_of_image = []
    # Create an image from the quadtree with specified depth and line display
    image = quadtree.createImage(custom_depth=8, show_lines=True)
    width, _ = image.size
    pixels = list(image.getdata())

    # Iterate through the pixels and convert color to hex format
    for i, color in enumerate(pixels):
        x = i % width  # Calculate the x-coordinate
        y = i // width  # Calculate the y-coordinate
        pixel_data_of_image.append(((x, y), rgbToHex(color)))

    return pixel_data_of_image
