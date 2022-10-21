if __name__ == "__main__":
    from rgb import RGB
else:
    from .rgb import RGB
from tqdm import tqdm
from numpy import average, array, ndarray


class WrongColorSpaceException(Exception):
    ...


def get_average_color(image) -> RGB:
    """
    Internal helper function to compute the average color of an image

    Parameters
    ----------
    image:
        The image whose average color we want to compute

    Returns
    -------
    tuple
        A color that contains the average color

    """

    avg_col_row = average(image, axis=0)
    avg_col = average(avg_col_row, axis=0)

    if not isinstance(avg_col, ndarray) or len(avg_col) < 3:
        raise WrongColorSpaceException("the image uses a different color space")

    return RGB(*map(round, avg_col))
    # cols = image.getcolors()
    # print("[COLS] debug:", cols)
    # _m = max(cols, key=lambda v, _: v)
    # return RGB(*_m)


if __name__ == "__main__":
    # TODO: load image, I just deleted the thing lmao
    from PIL import Image

    im = Image.open("./images/020A17.jpg")
    print(get_average_color(im))
    im.close()
