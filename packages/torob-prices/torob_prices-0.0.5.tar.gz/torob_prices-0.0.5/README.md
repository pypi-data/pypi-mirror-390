# Torob Prices

A simple web scraper to find the lowest price of a product on the Torob website.

## Installation

```bash
pip install torob-prices
```

## Usage

Run the script from your terminal:

```bash
torob-prices "your product name"
```

For example:

```bash
find-less-price "iphone 15 pro max"
```

### Options

*   `--min`: Only display the minimum price.
*   `--base_url`: Override the default search URL (`https://torob.com/search/`).

#### Example with options:

```bash
find-less-price "samsung s23 ultra" --min
```