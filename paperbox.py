#! /usr/bin/env python

"""
paperbox - Generate a pdf with the lines to cut and glue a paper box with the given dimensions.

Usage:
    paperbox.py <length> <width> <height> [--verbose=<level>] [--gap=<gap>] [--F=<output_folder>] [--o=<output_name>] [--m=<margin>]
    paperbox.py -h|--help
    paperbox.py --version

Description:
    <length>    Length of the box in centimeters, use point as decimal separator.
    <width>     Width of the box.
    <height>    Height of the box.

Options:
    -h,--help               show help.
    --verbose=<level>       verbose levels:
                            DEBUG=1, 
                            INFO=2, 
                            WARN=3, 
                            ERROR=4, 
                            CRITICAL=5 [default: 2].
    --gap=<gap>             Gap between the faces in milimeters [default: 0.75].
    --F=<output_folder>      Folder to save the pdf [default: .//].
    --o=<output_name>        Name of the pdf file [default: paper_box.pdf].
    --m=<margin>             Margin for x and y in centimeters [default: 0.5].
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
ALLOW_WARPING = True


# ----------------------------- #### --------------------------
def generate_paper_box(
    l: float,
    w: float,
    h: float,
    *,
    pagesize: tuple[float, float] = A4,
    output_folder=".//",
    output_name="paper_box.pdf",
    gap=0.075,
    cut_gap=0.25,
    x_offset=0.5,
    y_offset=0.5,
) -> None:
    """Generate a pdf with the lines to create a paper box with the given dimensions.
    It reorders the dimensions to be l >= w >= h.

    ## Parameters
    ``l``: length of the box.
    ``w``: width of the box.
    ``h``: height of the box.
    ``pagesize``: size of the page. Default is A4.
    ``output_folder``: folder where the pdf will be saved. Default is the current folder.
    ``output_name``: name of the pdf file. Default is "paper_box.pdf".
    ``gap``: gap between the faces. Default is 0.075 cm.
    ``cut_gap``: gap between main faces and cut faces. Default is 0.5 cm.
    ``x_offset``: margin for x. Default is 0.5 cm.
    ``y_offset``: margin for y. Default is 0.5 cm.

    ## Return
    None
    """

    # Reorder the dimensions
    l, w, h = sorted([l, w, h], reverse=True)
    logging.debug(
        f"Generating paper box with dimensions: {l} length, {w} width, {h} height."
    )

    # --- gapping condition
    GAPPING = gap > 0  # create gaps between the faces

    if GAPPING:
        l += 2 * gap
        w += 2 * gap
        h += 2 * gap

    # --- checking
    L_PAGE = pagesize[1] / 28.35  # conversion to cm
    W_PAGE = pagesize[0] / 28.35

    assert l >= w >= h > 0, "Dimmesion/s can not be zero."
    L_MAX = l * 2 + 3 * h

    if ALLOW_WARPING:
        if L_MAX >= L_PAGE:
            logging.warning(
                f"Length is too big {L_MAX:.2f} with maximum of {L_PAGE:.2f}. "
            )
    else:
        assert (
            L_MAX < L_PAGE
        ), f"Too big length or height. Occupied space can not be more than {L_PAGE:.2f} cm. Current is {L_MAX:.2f} cm."

    W_MAX = w + 2 * h
    logging.debug(f"Width is {W_MAX:.2f} and {W_PAGE:.2f}.")
    assert (
        W_MAX <= W_PAGE
    ), f"Too big width or height. Occupied space can not be more than {W_PAGE:.2f} cm. Current is {W_MAX:.2f} cm."

    # -- mid squares
    if make_long_mid_faces:
        # These faces are made the longest possible in order to have a larger surface area to glue.
        W_WIDE_MAX = W_PAGE - w - x_offset * 2
        W_WIDE = w + 2 * l
        w_mid = W_WIDE_MAX / 2
        if l > w_mid:
            logging.warning(
                f"Width of the mid faces is too big {W_WIDE:.2f} and {W_WIDE_MAX:.2f}. It will be reduced from {l:.2f} to {w_mid:.2f}."
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

    # cover
    c.setDash(4, 1)
    c.rect(x0 + cut_gap * cm, y0, (w - 2 * cut_gap) * cm, (h - cut_gap) * cm)
    c.setDash([])

    # ### ------- sides
    logging.debug("Drawing sides.")
    x0 = (x_offset + w_mid - h) * cm
    y0 = y_offset * cm

    c.setDash(1, 2)
    c.rect(
        x0 + cut_gap * cm,
        y0 + cut_gap * cm,
        (h - 2 * cut_gap) * cm,
        (h - cut_gap) * cm,
    )
    c.setDash([])

    # left side
    c.rect(x0, y0 + h * cm, h * cm, l * cm)

    x0 += (w + h) * cm

    c.setDash(1, 2)
    c.rect(
        x0 + cut_gap * cm,
        y0 + cut_gap * cm,
        (h - 2 * cut_gap) * cm,
        (h - cut_gap) * cm,
    )
    c.setDash([])

    # right side
    c.rect(x0, y0 + h * cm, h * cm, l * cm)

    # up side faces
    y0 += (l + h * 2) * cm

    c.setDash(4, 1)
    # up right face
    c.rect(x0, y0 + cut_gap * cm, (h - cut_gap) * cm, (l - 2 * cut_gap) * cm)
    x0 -= (w + h) * cm

    # up left face
    c.rect(
        x0 + cut_gap * cm, y0 + cut_gap * cm, (h - cut_gap) * cm, (l - 2 * cut_gap) * cm
    )
    c.setDash([])

    # mid faces
    c.setDash(1, 2)
    logging.debug("Drawing mid faces.")
    x0 = x_offset * cm
    y0 = (y_offset + h + l) * cm

    # left side
    c.rect(
        x0 + cut_gap * cm,
        y0 + cut_gap * cm,
        (w_mid - cut_gap) * cm,
        (h - 2 * cut_gap) * cm,
    )

    x0 = (x_offset + w_mid + w) * cm
    y0 = (y_offset + h + l) * cm

    # right side
    c.rect(
        x0,
        y0 + cut_gap * cm,
        (w_mid - cut_gap) * cm,
        (h - 2 * cut_gap) * cm,
    )
    c.setDash([])

    # ----- GAPPING
    if not GAPPING:
        logging.info("Saving pdf.")
        c.save()
        return

    # ----- GAPPING
    # Executes everything again but with gaps
    logging.debug("Drawing main faces with gaps.")
    l -= 2 * gap
    w -= 2 * gap
    h -= 2 * gap
    x0 = (x_offset + w_mid + gap) * cm
    y0 = (y_offset + gap) * cm

    c.rect(x0, y0, w * cm, h * cm)
    y0 += (h + 2 * gap) * cm
    c.rect(x0, y0, w * cm, l * cm)
    y0 += (l + 2 * gap) * cm
    c.rect(x0, y0, w * cm, h * cm)
    y0 += (h + 2 * gap) * cm
    c.rect(x0, y0, w * cm, l * cm)

    logging.info("Saving pdf.")
    c.save()
    return


if __name__ == "__main__":
    args = docopt(
        doc=__doc__,
        version="1.1",
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

    gap = float(args["--gap"]) / 10  # from mm to cm
    output_folder = args["--F"]
    output_name = args["--o"]
    generate_paper_box(
        l,
        w,
        h,
        gap=gap,
        output_folder=output_folder,
        output_name=output_name,
        x_offset=float(args["--m"]),
        y_offset=float(args["--m"]),
    )
