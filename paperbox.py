#! /usr/bin/env python

"""
paperbox - Generate a pdf with the lines to create a paper box with the given dimensions.

Usage:
    paperbox.py <length> <width> <height> [--verbose=<level>]
    paperbox.py -h|--help
    paperbox.py --version

Description:
    <length>    Length of the box in centimeters, use point as decimal separator.
    <width>     Width of the box.
    <height>    Height of the box.

Options:
    -h,--help               show help.
    --verbose <level>       verbose levels:
                            DEBUG=1, 
                            INFO=2, 
                            WARN=3, 
                            ERROR=4, 
                            CRITICAL=5 [default: 2].
"""

"""
Python 3
29 / 07 / 2024
@author: z_tjona

"I find that I don't understand things unless I try to program them."
-Donald E. Knuth
"""


# ----------------------------- logging --------------------------
import logging
from sys import stdout
from datetime import datetime


# ----------------------------- #### --------------------------
from docopt import docopt

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

make_long_mid_faces = True
x_offset = 0.5  # in cm
y_offset = 1  # in cm


# ----------------------------- #### --------------------------
def generate_paper_box(
    l: float,
    w: float,
    h: float,
    *,
    pagesize: tuple[float, float] = A4,
    output_folder=".//",
    output_name="paper_box.pdf",
) -> None:
    """Generate a pdf with the lines to create a paper box with the given dimensions.
    It reorders the dimensions to be l >= w >= h.

    ## Parameters
    ``l``: length of the box.
    ``w``: width of the box.
    ``h``: height of the box.

    ## Return
    None

    """

    # Reorder the dimensions
    l, w, h = sorted([l, w, h], reverse=True)
    logging.debug(
        f"Generating paper box with dimensions: {l} length, {w} width, {h} height."
    )

    # --- checking

    L_PAGE = pagesize[1] / 28.35  # conversion to cm
    W_PAGE = pagesize[0] / 28.35

    assert l >= w >= h > 0, "Dimmesion/s can not be zero."
    L_MAX = l * 2 + 3 * h

    assert (
        L_MAX < L_PAGE
    ), f"Too big length or height. Occupied space can not be more than {L_PAGE} cm. Current is {L_MAX} cm."

    W_MAX = w + 2 * h
    assert (
        W_MAX <= W_PAGE
    ), f"Too big width or height. Occupied space can not be more than {W_PAGE} cm. Current is {W_MAX} cm."

    # -- mid squares
    if make_long_mid_faces:
        # These faces are made the longest possible in order to have a larger surface area to glue.
        W_WIDE_MAX = W_PAGE - w - x_offset * 2
        W_WIDE = w + 2 * l
        w_mid = W_WIDE_MAX / 2
        if l > w_mid:
            logging.warning(
                f"Width of the mid faces is too big {W_WIDE} and {W_WIDE_MAX}. It will be reduced from {l} to {w_mid}."
            )
        else:
            w_mid = l

    # --- drawing
    full_file_path = output_folder + output_name
    logging.info(f"Generating paper box in {full_file_path}.")
    c = canvas.Canvas(full_file_path, pagesize=A4)

    # main faces
    logging.debug("Drawing main faces.")
    x0 = (x_offset + w_mid) * cm
    y0 = y_offset * cm

    c.rect(x0, y0, w * cm, h * cm)
    y0 += h * cm
    c.rect(x0, y0, w * cm, l * cm)
    y0 += l * cm
    c.rect(x0, y0, w * cm, h * cm)
    y0 += h * cm
    c.rect(x0, y0, w * cm, l * cm)
    y0 += l * cm
    c.rect(x0, y0, w * cm, h * cm)

    # sides
    logging.debug("Drawing sides.")
    x0 = (x_offset + w_mid - h) * cm
    y0 = y_offset * cm

    c.rect(x0, y0, h * cm, (l + h) * cm)
    x0 += (w + h) * cm
    c.rect(x0, y0, h * cm, (l + h) * cm)

    y0 += (l + h * 2) * cm
    c.rect(x0, y0, h * cm, l * cm)
    x0 -= (w + h) * cm
    c.rect(x0, y0, h * cm, l * cm)

    # mid faces
    logging.debug("Drawing mid faces.")
    x0 = x_offset * cm
    y0 = (y_offset + h + l) * cm

    c.rect(x0, y0, w_mid * cm, h * cm)

    x0 = (x_offset + w_mid + w) * cm
    y0 = (y_offset + h + l) * cm

    c.rect(x0, y0, w_mid * cm, h * cm)

    logging.info("Saving pdf.")
    c.save()
    return


if __name__ == "__main__":
    args = docopt(
        doc=__doc__,
        version="1",
    )
    print(args)
    if args["--verbose"] == "1":
        _level = logging.DEBUG
    elif args["--verbose"] == "2":
        _level = logging.INFO
    elif args["--verbose"] == "3":
        _level = logging.WARN
    elif args["--verbose"] == "4":
        _level = logging.ERROR
    elif args["--verbose"] == "5":
        _level = logging.CRITICAL

    logging.basicConfig(
        level=_level,
        format="[%(asctime)s][%(levelname)s] %(message)s",
        stream=stdout,
        datefmt="%m-%d %H:%M:%S",
    )
    logging.debug(f"Started at {datetime.now()}")

    l = float(args["<length>"])
    w = float(args["<width>"])
    h = float(args["<height>"])

    generate_paper_box(l, w, h)