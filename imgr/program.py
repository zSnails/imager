from argparse import ArgumentParser, Namespace
from typing import List, Dict
from numpy import array
from PIL.Image import open as im_open, new as im_new

# from PIL import Image
from os import listdir
from os.path import join
from random import choice
from .rgb import RGB


def _parse_args(*arguments: List[str]) -> Namespace:
    """
    Helper function to parse arguments, the only purpose for this function
    is so the run function doesn't look too polluted

    Parameters
    ----------
    arguments : List[str]
        A list of arguments to parse, preferably from argv

    Returns
    -------
    Namespace
        An arguments namespace, I'm not really sure why it's called like this though
    """

    parser = ArgumentParser(description="TODO: document this")

    parser.add_argument("image", type=str, help="The image to be converted")
    parser.add_argument("--img-dir", type=str, default="./images", required=False)

    return parser.parse_args()


def im_free(computed: Dict[RGB, List[RGB]]) -> None:
    for val in computed.values():
        # for img in val:
        val.close()


# NOTE: no need to specify image width or height
OUT_SIZE = 50 


def run(*arguments: List[str]) -> None:
    """
    Runs the main process for the program

    Parameters
    ----------
    arguments : List[str]
        A list of arguments to be parsed, preferably from sys.argv

    Returns
    -------
        None
    """

    args = _parse_args(arguments)

    print("debug: opening old image")
    im_orig = im_open(args.image, "r", formats=("JPEG", "PNG"))
    print("debug:", im_orig)

    print("debug: creating new image")

    dimensions = (
        im_orig.size[0] * OUT_SIZE,
        im_orig.size[1] * OUT_SIZE,
    )

    _im_new = im_new(mode="RGB", size=dimensions)
    print("debug:", _im_new)

    print("debug: created new image")
    found_cols = [[a, b, c] for a, b, c, *_ in list(set(im_orig.getdata()))]

    computed = _compute_values(args.img_dir, found_cols)

    pixels = im_orig.getdata()

    print("debug:", len(pixels))
    im_pos = [0, 1]

    found_computed = [array(col) for col in computed.keys()]

    try:
        cont = 0
        for idx, pixel in enumerate(tqdm(pixels)):
            if cont - 1 == _im_new.size[0]:
                im_pos[0] = 0
                im_pos[1] *= OUT_SIZE
                cont = 0

            pix = RGB(*pixel)

            _im_new.paste(
                computed[nearest_color(pix, found_computed)], box=(*im_pos,)
            )

            im_pos[0] += OUT_SIZE
            cont += 3

    finally:
        print("debug: freeing resources")
        im_orig.close()
        _im_new.save("lmao.jpg")
        _im_new.close()
        im_free(computed)


from .overall_color import get_average_color, WrongColorSpaceException
from .classify import nearest_color
from tqdm import tqdm

MAX_LEN = 200000


def _compute_values(dir: str, colors) -> None:
    """
    Loads every single image inside of the images folder and computes their average
    color, then stores it in a dictionary which contains some predefined basic color
    values

    Parameters
    ----------

    Returns
    -------
        None
    """

    computed = {}

    print("debug: indexing dir")
    print("debug: loading images")
    for file in tqdm(listdir(dir)):
        image = im_open(join(dir, file))

        if image is None:
            continue
        elif len(image.getdata()) > MAX_LEN:
            image.close()
            continue

        image = image.resize((OUT_SIZE, OUT_SIZE))

        try:
            ov_col = get_average_color(image)
        except WrongColorSpaceException:
            image.close()
            continue

        nearest = nearest_color(ov_col, colors)
        if not computed.get(nearest):
            computed.setdefault(nearest, image)
        # else:
        #     computed[nearest].append(image)
    else:
        print("debug: image computation finished without any errors")

    return computed


# if __name__ == "__main__":
#     from sys import argv

#     run(argv)
