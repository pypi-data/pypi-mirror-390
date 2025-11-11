import subprocess
from pathlib import Path
from typing import Literal

import typer
from pypdf import PdfWriter
from pypdf.generic import RectangleObject

MM_IN = 0.0393701
IN_PT = 72
MM_PT = MM_IN * IN_PT

Rectangle = tuple[float, float, float, float]


def parse_gs_output(gs_output: str) -> list[Rectangle]:
    result = []
    for line in gs_output.splitlines()[1::2]:
        if line.startswith("%%HiResBoundingBox:"):
            _, left, bottom, right, top = line.split()
            result.append((float(left), float(bottom), float(right), float(top)))
    return result


def get_target_mediabox(
    bounding_box: Rectangle,
    margin_left: float,
    margin_top: float,
    page_size_x: float,
    page_size_y: float,
) -> Rectangle:
    left, bottom, right, top = bounding_box

    target_left = left - margin_left
    target_top = top + margin_top
    target_bottom = target_top - page_size_y
    target_right = target_left + page_size_x

    # If the content does not fit on the target page size, we increase the
    # latter. In this case, we add small right and bottom margins, because
    # ghostscript bounding boxes can be imprecise and crop off content.
    if target_right < right:
        target_right = right + MM_PT
    if target_bottom > bottom:
        target_bottom = bottom - MM_PT

    return (target_left, target_bottom, target_right, target_top)


app = typer.Typer()


@app.command()
def main(
    pdf_input_path: Path,
    margin_left: float,
    margin_top: float,
    page_size_x: float,
    page_size_y: float,
    pdf_output_path: Path | None = None,
    unit: Literal["pt", "mm"] = "pt",
):
    pdf_output_path = pdf_output_path or Path(
        pdf_input_path.stem + "_out" + pdf_input_path.suffix
    )
    if unit == "mm":
        margin_left *= MM_PT
        margin_top *= MM_PT
        page_size_x *= MM_PT
        page_size_y *= MM_PT

    print("Running ghostscript to get bounding boxes...")
    try:
        gs_result = subprocess.run(
            ["gs", "-dSAFER", "-dNOPAUSE", "-dBATCH", "-sDEVICE=bbox", pdf_input_path],
            capture_output=True,
            check=True,
            encoding="utf-8",
        )
    except FileNotFoundError as e:
        print("The ghostscript executable `gs` could not be found.")
        raise e

    bounding_boxes = parse_gs_output(gs_result.stderr)

    print("Setting margins...")
    writer = PdfWriter(pdf_input_path)
    for page, bounding_box in zip(writer.pages, bounding_boxes):
        target_mediabox = RectangleObject(
            get_target_mediabox(
                bounding_box, margin_left, margin_top, page_size_x, page_size_y
            )
        )
        page.artbox = target_mediabox
        page.bleedbox = target_mediabox
        page.cropbox = target_mediabox
        page.mediabox = target_mediabox
        page.trimbox = target_mediabox

    writer.write(pdf_output_path)
    print(f"Done. Output written to {pdf_output_path}")


if __name__ == "__main__":
    app()
