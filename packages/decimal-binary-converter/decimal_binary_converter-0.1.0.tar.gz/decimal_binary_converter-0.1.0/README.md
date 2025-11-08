# decimal_binary_converter

A Python package to convert numbers between decimal and binary representations.

## Features

- Convert decimal to binary with `decimal_to_binary`
- Convert binary to decimal with `binary_to_decimal`

## Installation

Copy the `dec_bi_conv` folder into your project or use `pip install .` from the root folder.

## Usage 
from dec_bi_conv import decimal_to_binary, binary_to_decimal

print(decimal_to_binary(15)) # '1111'
print(binary_to_decimal('1111')) # 15


## Testing

Run tests using pytest:
pytest tests/


## License

See LICENSE.txt for terms.
