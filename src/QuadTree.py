from .Quadrant import *


class QuadTree:
    def __init__(self, image):
        """
        Initialize a quadtree for partitioning an image.

        Args:
            image (PIL.Image): The image to be processed and partitioned into quadrants.
        """
        self.width, self.height = image.size  # Store the dimensions of the image.
        self.max_depth = 0  # Initialize the maximum depth of the quadtree.
        self.start(image)  # Begin building the quadtree with the given image.

    def start(self, image):
        """
        Start the quadtree construction by creating the root quadrant.

        Args:
            image (PIL.Image): The original image used for the quadtree.
        """
        self.root = Quadrant(image, image.getbbox(), 0)  # Create the root quadrant.
        self.build(self.root, image)  # Build the quadtree starting from the root.

    def build(self, root, image):
        """
        Recursively build the quadtree structure from a given root quadrant.

        Args:
            root (Quadrant): The current root quadrant to split and build upon.
            image (PIL.Image): The original image used for cropping quadrants.
        """
        # Check if the maximum depth is reached or detail threshold is met.
        if root.depth >= MAX_DEPTH or root.detail <= DETAIL_THRESHOLD:
            if root.depth > self.max_depth:
                self.max_depth = root.depth  # Update the maximum depth if necessary.
            root.leaf = True  # Mark this quadrant as a leaf node.
            return  # Stop further splitting.

        root.splitQuadrant(image)  # Split the current quadrant into child quadrants.

        # Use a thread pool to build child quadrants in parallel.
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self.build, child, image) for child in root.children
            ]
            concurrent.futures.wait(futures)  # Wait for all threads to complete.

    def createImage(self, custom_depth, show_lines=False):
        """
        Create an image representation of the quadtree at a specified depth.

        Args:
            custom_depth (int): The depth level for which to create the image.
            show_lines (bool): Flag to indicate whether to draw outlines around quadrants.

        Returns:
            PIL.Image: An image representing the state of the quadtree at the specified depth.
        """
        image = Image.new("RGB", (self.width, self.height))  # Create a new blank image.
        draw = ImageDraw.Draw(image)  # Prepare to draw on the image.
        draw.rectangle(
            (0, 0, self.width, self.height), (0, 0, 0)
        )  # Fill the image with black.

        leaf_quadrants = self.getLeafQuadrants(
            custom_depth
        )  # Get leaf quadrants at the specified depth.

        # Draw each leaf quadrant on the image.
        for quadrant in leaf_quadrants:
            draw.rectangle(
                quadrant.bbox,
                quadrant.colour,
                outline=(0, 0, 0) if show_lines else None,  # Outline if requested.
            )

        return image  # Return the constructed image.

    def getLeafQuadrants(self, depth):
        """
        Retrieve all leaf quadrants at a specified depth.

        Args:
            depth (int): The depth level to retrieve leaf quadrants.

        Raises:
            ValueError: If the specified depth exceeds the maximum depth of the tree.

        Returns:
            list: A list of leaf quadrants at the specified depth.
        """
        if depth > self.max_depth:
            raise ValueError(
                "A depth larger than the tree's depth was given"
            )  # Check for valid depth.
        quadrants = []  # List to store the leaf quadrants.
        self.recursiveSearch(
            self.root, depth, quadrants.append
        )  # Search for leaf quadrants.
        return quadrants  # Return the found quadrants.

    def recursiveSearch(self, quadrant, max_depth, append_leaf):
        """
        Recursively search for leaf quadrants at a specific depth.

        Args:
            quadrant (Quadrant): The current quadrant being searched.
            max_depth (int): The target depth for leaf quadrants.
            append_leaf (callable): A function to append found leaf quadrants to a list.
        """
        # Check if the current quadrant is a leaf or at the target depth.
        if quadrant.leaf or quadrant.depth == max_depth:
            append_leaf(quadrant)  # Add the quadrant to the list of leaves.
        elif (
            quadrant.children
        ):  # Continue searching through child quadrants if available.
            for child in quadrant.children:
                self.recursiveSearch(child, max_depth, append_leaf)

    def createGif(self, file_name, duration=1000, loop=0, show_lines=False):
        """
        Create a GIF representation of the quadtree's state over different depths.

        Args:
            file_name (str): The file name for saving the GIF.
            duration (int): Duration of each frame in milliseconds.
            loop (int): Number of times the GIF should loop (0 for infinite).
            show_lines (bool): Flag to indicate whether to show outlines around quadrants.
        """
        gif = []  # List to store images for GIF frames.
        end_product_image = self.createImage(
            self.max_depth, show_lines=show_lines
        )  # Create the final image.

        # Create frames for each depth from 0 to max_depth.
        for i in range(self.max_depth):
            image = self.createImage(
                i, show_lines=show_lines
            )  # Create image for the current depth.
            gif.append(image)  # Add to the GIF frames list.

        # Add the end product image multiple times to the end of the GIF.
        gif.extend([end_product_image] * 4)

        # Save the constructed GIF with the specified parameters.
        gif[0].save(
            file_name,
            save_all=True,
            append_images=gif[1:],
            duration=duration,
            loop=loop,
        )
