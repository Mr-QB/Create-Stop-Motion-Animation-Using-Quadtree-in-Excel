from src.utility import *


class Quadrant:
    def __init__(self, image, bbox, depth):
        """
        Initialize a quadrant of an image for a quadtree structure.

        Args:
            image (PIL.Image): The original image to be processed.
            bbox (tuple): A bounding box defining the area of this quadrant in the format (left, top, right, bottom).
            depth (int): The depth of this quadrant in the quadtree structure.
        """
        self.bbox = bbox  # The bounding box of the quadrant.
        self.depth = depth  # The depth level of this quadrant in the quadtree.
        self.children = None  # Placeholder for child quadrants after splitting.
        self.leaf = False  # Flag to indicate if this quadrant is a leaf node.

        image = image.crop(bbox)  # Crop the image to the bounding box of the quadrant.
        hist = image.histogram()  # Obtain the histogram of the cropped image.
        self.detail = getDetail(hist)  # Calculate detail level from histogram.
        self.colour = averageColour(image)  # Compute the average color of the quadrant.

    def splitQuadrant(self, image):
        """
        Split the current quadrant into four child quadrants.

        Args:
            image (PIL.Image): The original image used for cropping quadrants.
        """
        left, top, width, height = self.bbox
        # Calculate midpoints to divide the bounding box into four smaller quadrants.
        middle_x = left + (width - left) // 2
        middle_y = top + (height - top) // 2

        # Create four child quadrants by cropping the original image based on midpoints.
        self.children = [
            Quadrant(image, (left, top, middle_x, middle_y), self.depth + 1),
            Quadrant(image, (middle_x, top, width, middle_y), self.depth + 1),
            Quadrant(image, (left, middle_y, middle_x, height), self.depth + 1),
            Quadrant(image, (middle_x, middle_y, width, height), self.depth + 1),
        ]
