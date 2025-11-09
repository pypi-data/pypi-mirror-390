# Torob Less Price Finder

A simple web scraper to find the lowest price of a product on the Torob website.

## Installation

```bash
pip install torob-prices
```

## Usage

You need to create a `.env` file in the directory you are running the command from, with the following content:

```
BASE_URL=https://torob.com/search/
```

Then you can run the script from your terminal:

```bash
find-less-price "your product name"
```

For example:

```bash
find-less-price "iphone 15 pro max"
```
