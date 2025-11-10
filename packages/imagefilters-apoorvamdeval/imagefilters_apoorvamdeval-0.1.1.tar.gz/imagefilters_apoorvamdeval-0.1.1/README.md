# imagefilters-apoorvamdeval

A simple image filtering package supporting five filters:
- Averaging
- Gaussian
- Weighted Average
- Median

## Installation
pip install imagefilters-apoorvamdeval

## Usage
from imagefilters import apply_filter

# Basic usage:
apply_filter("path/to/image.jpg")

# Specify filter type (averaging / gaussian / median / weighted / average):

apply_filter("path/to/image.jpg", filter_type=" ")

# Specify filter and kernel size (use odd sizes like 3, 5, 7):
apply_filter("path/to/image.jpg", filter_type=" ", kernel_size=x)
