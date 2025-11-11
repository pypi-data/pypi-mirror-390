# `set-pdf-margins`

This script places user-defined margins around the content of each page of a given PDF file. The left and top margins are given explicitly. The right and bottom margins result from explicitly given page sizes in horizontal (x) and vertical (y) directions. The page content is not rescaled. The document outline is preserved. This script is meant to facilitate PDF reading and margin note taking on tablets and e-readers. Note that correctly determining the bounding box of the content of a PDF page is difficult and your mileage may vary depending on your input PDF.

**Usage**:

```console
$ set-pdf-margins [OPTIONS] PDF_INPUT_PATH MARGIN_LEFT MARGIN_TOP PAGE_SIZE_X PAGE_SIZE_Y
```

**Arguments**:

* `PDF_INPUT_PATH`: [required]
* `MARGIN_LEFT`: [required]
* `MARGIN_TOP`: [required]
* `PAGE_SIZE_X`: [required]
* `PAGE_SIZE_Y`: [required]

**Options**:

* `--pdf-output-path PATH`
* `--unit [pt|mm]`: [default: pt]
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

If your page content is too large to fit on your target page size, or if you want to crop headers, footers, or page numbers before determining the bounding boxes of the actual content of each page, consider preprocessing your file using other tools first.
