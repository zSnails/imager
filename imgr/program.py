from argparse import ArgumentParser, Namespace
from typing import List, Dict, Tuple
from numpy import array
from PIL.Image import open as im_open, new as im_new, Image
from pyvips import Image

from datetime import datetime
from multiprocessing import Process, Pipe
from multiprocessing.connection import Connection

# from PIL import Image
from os import listdir
from os.path import join
from random import choice
from .rgb import RGB


def chunk(_list: list, size: int):
    """
    Chunks and yields chunks of *n* size

    Parameters
    ----------
    _list : list
        Any list that needs to be chunked
    size : int
        The size of each individual chunk
    """

    for i in range(0, len(_list), size):
        yield _list[i : i + size]


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
    parser.add_argument("--num-processess", type=int, default=4, required=False)

    return parser.parse_args()


def im_free(computed: Dict[RGB, List[RGB]]) -> None:
    """
    Closes all the open file pointers to each image that was used

    Parameters
    ----------
    computed : Dict[RGB, List[RGB]]
        The dictionary that contains all used images

    Returns
    -------
        None
    """
    for val in computed.values():
        val.close()


# NOTE: no need to specify image width or height
OUT_SIZE = 50


def generate_image_block(
    id: int,
    pixels: List[Tuple[int, int, int]],
    colors: List[RGB],
    images: Dict[RGB, Image],
    dimensions: Tuple[int, int],
    out: Connection,
):
    im_pos = [0, 0]
    _im_new = im_new("RGB", dimensions)
    print(f"debug: generating image: {id}")
    for idx, pixel in enumerate(tqdm(pixels)):
        if (idx + 1) % dimensions[0] == 0:
            im_pos[0] = 0
            im_pos[1] += OUT_SIZE

        pix = RGB(*pixel)

        _im_new.paste(images[nearest_color(pix, colors)], box=(*im_pos,))

        im_pos[0] += OUT_SIZE

    print("debug: sending data")
    out.send((id, list(_im_new.getdata())))
    _im_new.close()
    print("debug: sent data")


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

    print("debug: opening image")
    im_orig = im_open(args.image, "r", formats=("JPEG", "PNG"))

    print("debug: creating new image")

    found_cols = [[a, b, c] for a, b, c, *_ in list(set(im_orig.getdata()))]

    # apply multiprocessing to this section
    print("debug: computing images")

    COLOR_CHUNK_SZ = len(found_cols) // args.num_processess

    # this is probably a bit overkill imo
    files = list(map(lambda el: join(args.img_dir, el), listdir(args.img_dir)))
    IMAGE_CHUNK_SZ = len(files) // args.num_processess

    image_chunks = chunk(files, IMAGE_CHUNK_SZ)
    color_chunks = chunk(found_cols, IMAGE_CHUNK_SZ)

    pool = []

    out, value = Pipe()

    for _ in range(args.num_processess):
        p = Process(
            target=compute_images,
            args=(next(image_chunks), next(color_chunks), out),
        )

        p.start()

        pool.append(p)

    computed = {}
    print("debug: waiting for results")
    for _ in range(args.num_processess):
        data = value.recv()
        computed = {**computed, **data}
    value.close()

    print("debug: waiting for each individual process")
    for process in pool:
        process.join()

    # _compute_images(args.img_dir, found_cols, computed)

    pixels = im_orig.getdata()

    found_computed = [array(col) for col in computed.keys()]

    print("debug: finished all computation")
    dimensions = (
        im_orig.size[0] * OUT_SIZE,
        im_orig.size[1] * OUT_SIZE,
    )

    try:

        out, img_data = Pipe()
        IM_CHUNKS = args.num_processess

        CHUNK_HEIGHT = dimensions[1] // IM_CHUNKS

        print("debug: created new image")

        pixel_chunk = chunk(list(pixels), IM_CHUNKS)
        gen_pool = []
        for id in range(IM_CHUNKS):
            p = Process(
                target=generate_image_block,
                args=(
                    id,
                    next(pixel_chunk),
                    found_computed,
                    computed,
                    (dimensions[0], CHUNK_HEIGHT),
                    out,
                ),
            )
            p.start()
            gen_pool.append(p)

        final_image_data = {}
        for _ in range(IM_CHUNKS):
            print("debug: waiting for chunk data")
            id, data = img_data.recv()
            print("debug: received chunk data")
            final_image_data[id] = data

        img_data.close()

        _out_arr = []
        for id in range(IM_CHUNKS):
            _out_arr.append(final_image_data[id])

        out = Image.new_from_array(_out_arr, interpretation="auto")
        out.write_to_file(str(datetime.now()) + ".jpg")

        for proc in gen_pool:
            proc.join()
    finally:
        print("debug: freeing resources")
        im_orig.close()
        im_free(computed)


from .overall_color import get_average_color, WrongColorSpaceException
from .classify import nearest_color
from tqdm import tqdm

MAX_LEN = 200000


def compute_images(files: List[str], colors: List[Tuple[int, int, int]], out) -> None:
    """
    Loads every single image inside of the images folder and computes their average
    color, then stores it in a dictionary which contains some predefined basic color
    values

    Parameters
    ----------
    dir : str
        The directory for reading images
    colors : List[RGB]
        A list of colors that need to have a certain image to be found
    out : Dict[RGB, Image]
        A dict to store output images
    Returns
    -------
        None
    """

    print("debug: loading images")

    computed = {}
    for file in tqdm(files):
        image = im_open(file)

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
    else:
        print("debug: image computation finished without any errors")

    out.send(computed)


# if __name__ == "__main__":
#     from sys import argv

#     run(argv)
