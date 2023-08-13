import math

earthCir = 40075016.686
degreesPerMeter = 360 / earthCir


class Map():

    def __init__(self, map_data):
        self.latitude = map_data["latitude"]
        self.longitude = map_data["longitude"]
        self.zoom = map_data["zoom"]
        self.width = map_data["width"]
        self.height = map_data["height"]

    # Converts to radians from Deg
    def toRadians(self, degrees):
        return (degrees * math.pi/180)

    # Calculates the bounding box of what is displayed
    def calculate_bounding_box(self):
        metersPerPixelEW = earthCir / math.pow(2, self.zoom + 8)
        metersPerPixelNS = earthCir / \
            math.pow(2, self.zoom + 8) * \
            math.cos(self.toRadians(self.latitude))

        shiftMetersEW = self.width/2 * metersPerPixelEW
        shiftMetersNS = self.height/2 * metersPerPixelNS

        shiftDegreesEW = shiftMetersEW * degreesPerMeter
        shiftDegreesNS = shiftMetersNS * degreesPerMeter

        return (self.latitude-shiftDegreesNS), (self.longitude-shiftDegreesEW), (self.latitude+shiftDegreesNS), (self.longitude+shiftDegreesEW)

    # Printing all data
    def print_map_data(self):

        south, west, north, east = self.calculate_bounding_box()

        print(f"latitude:   {self.latitude}\n",
              f"longitude:  {self.longitude}\n",
              f"zoom:       {self.zoom}\n"
              f"topLeft:    {north},{west}\n"
              f"botLeft:    {south},{west}\n",
              f"topRight:   {north},{east}\n",
              f"botRight:   {south},{east}",
              f"resolution: {self.width}x{self.height}")