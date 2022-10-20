from argparse import ArgumentParser, Namespace
from typing import List
from PIL import Image
from os import listdir
from os.path import join


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

    computed = _compute_values(args.img_dir)

    im_orig = Image.open(args.image, "r", formats=("JPEG", "PNG"))

    im_new = Image.new(mode="RGB", size=im_orig.size)

    # TODO: this is the part that we should make multithreaded
    # this is probably one of the easiest projects I've ever been given 💀💀
    
    # TODO: here goes the new image generation

    # END

    im_orig.close()
    im_new.save("lmao.png")
    im_new.close()


from .overall_color import get_average_color, WrongColorSpaceException
from .classify import nearest_color
from tqdm import tqdm
from numpy import where

MAX_LEN = 200000


def _compute_values(dir: str) -> None:
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
        image = Image.open(join(dir, file))
        if image is None:
            continue
        elif len(image.getdata()) > MAX_LEN:
            continue

        try:
            ov_col = get_average_color(image)
        except WrongColorSpaceException:
            continue

        nearest = nearest_color(ov_col)
        if not computed.get(nearest):
            computed.setdefault(nearest, [image])
        else:
            computed[nearest].append(image)
    else:
        print("debug: image computation finished without any errors")

    return computed


# if __name__ == "__main__":
#     from sys import argv

#     run(argv)
