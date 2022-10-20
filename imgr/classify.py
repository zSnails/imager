from .rgb import RGB
from numpy import array, sqrt, sum, where, amin

COLORS = [
    [255, 0, 0],  # red
    [255, 89, 0],  # orange
    [255, 200, 0],  # yellow
    [0, 255, 0],  # green
    [0, 255, 217],  # celest
    [0, 0, 255],  # blue
    [166, 0, 255],  # purple
    [255, 0, 187],  # pink
]


def nearest_color(color: RGB) -> RGB:
    """
    Computes the nearest color from a list of basic colors

    Parameters
    ----------
    color : RGB
        The color whose nearest you want to compute

    Returns
    -------
    RGB
        The nearest rgb value in the colors list
    """
    color = array(color)
    colors = array(COLORS)
    distances = sqrt(sum((colors - color) ** 2, axis=1))
    smallest = where(distances == amin(distances))
    return RGB(*colors[smallest][0])


if __name__ == "__main__":
    red = RGB(0x00, 0x00, 0x3B)
    print(nearest_color(red))
