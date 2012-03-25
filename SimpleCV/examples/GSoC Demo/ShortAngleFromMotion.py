from SimpleCV import *

class MotionDetector:
    """Detects motion between frames."""
    def __init__(self, strategy):
        """Constructs a MotionDetector with the supplied strategy."""
        self.concrete_strategy = None
        if strategy:
            self.concrete_strategy = strategy()

    def isMoving(self, new_image, old_image):
        """Implements the algorithm of the supplied strategy."""
        if self.concrete_strategy:
            return self.concrete_strategy.isMoving(new_image, old_image)
        else:
            return False

class MotionDetectorByBlobs:
    """Detects motion by blob detection on frame diffrencing."""
    def isMoving(self, new_image, old_image):
        difference_image = new_image - old_image
        if difference_image.findBlobs(-1, threshblocksize=99):
            # Using adapative blob detection
            # If difference_image has blobs then movement occurred
            return True
        else:
            return False

class ROI:
    """Region of Interest, coors and size we want to analyze from an image."""
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.height = height
        self.width = width

class ROIHandler:
    """Groups all the Regions Of Interest (ROI) and checks them for movement"""
    def __init__(self, md_strategy):
        self.MotionDetector = MotionDetector(strategy=md_strategy)
        self.ROIDict = {}

    def MapRegionToFunc(self, newROI, func):
        """Adds a new ROI to the handler and maps a function to it."""
        self.ROIDict[newROI] = func

    def getRegionsMoving(self, new_image, old_image):
        """Returns a list with all the ROI that have movement."""
        ROI_with_movement = []
        for r in self.ROIDict.keys():
            if (self.CheckRegionFits(r, new_image) and
                self.CheckRegionFits(r, old_image)):
                new_subimage = new_image.crop(r.x, r.y, r.width, r.height)
                old_subimage = old_image.crop(r.x, r.y, r.width, r.height)
                if self.MotionDetector.isMoving(new_subimage, old_subimage):
                    ROI_with_movement.append(r)
            else:
                print "Error: Region out of bounds of Image"
        return ROI_with_movement

    def ExecRegionFunc(self, region, image):
        """Executes the function mapped to a ROI."""
        return self.ROIDict[region](region, image)

    def ExecMovingRegionFuncs(self, new_image, old_image):
        """Executes the functions mapped to the ROI with movement."""
        moving = self.getRegionsMoving(new_image, old_image)
        for m in moving:
            self.ExecRegionFunc(m, old_image)

    def CheckRegionFits(self, region, image):
        """Checks if the ROI fits in the given image, returns boolean."""
        region_total_height = region.y + region.height
        region_total_width = region.x + region.width
        if (region_total_height <= image.height and
            region_total_width <= image.width):
            return True
        else:
            return False

from math import degrees, atan2

def getRectangleCenter(width, height):
    """Returns a tuple with the coordinates of the center of the rectangle."""
    return (width / 2, height / 2)

def getAngleFromCenter(region=None, image=None):
    """Prints the angle (from the center of the image) of the ROI activated."""
    if region and image:
        region_center = getRectangleCenter(region.width, region.height)
        image_center = getRectangleCenter(image.width, image.height)
        region_center_x, region_center_y = region_center
        region_center_x = region_center_x + region.x
        region_center_y = region_center_y + region.y
        image_center_x, image_center_y = image_center
        dy = region_center_y - image_center_y
        dx = region_center_x - image_center_x
        angle = degrees(atan2(dy, dx))
        print angle

def main():
    cam1 = VirtualCamera("bg.jpg", "image")
    cam2 = VirtualCamera("invert.jpg", "image")
    img1 = cam1.getImage()
    img2 = cam2.getImage()
    newROI = ROI(90, 220, 60, 50)
    handler = ROIHandler(md_strategy=MotionDetectorByBlobs)
    handler.MapRegionToFunc(newROI, getAngleFromCenter)
    handler.ExecMovingRegionFuncs(img1, img2)

main()
