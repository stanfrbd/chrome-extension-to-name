# Chrome Extension Name Fetcher

This project provides a Python script to fetch the names of Chrome extensions using their IDs. \
It supports fetching names for single or multiple extensions and exporting the results to CSV, Excel, or JSON formats.

## Features

- Fetch the name of a Chrome extension using its ID.
- Supports Edge extensions as well.
- Support for fetching names of multiple extensions from a file.
- Export results to CSV, Excel, or JSON formats.
- Proxy support for requests.

## Requirements

- Python 3.6+
- `requests`
- `beautifulsoup4`
- `aiohttp`
- `pandas`
- `xlsxwriter`

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/stanfrbd/chrome-extension-to-name.git
    cd chrome-extension-to-name
    ```

2. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

### Fetching a Single Extension Name

To fetch the name of a single Chrome extension using its ID:
```sh
python chrome-extension-to-name.py <extension_id> [-p <proxy>]
```

### Fetching Multiple Extension Names from a File

To fetch the names of multiple Chrome extensions from a file containing their IDs:
```sh
python chrome-extension-to-name.py -f <file_path> [-p <proxy>] [--csv <output_csv>] [--excel <output_excel>] [--json <output_json>]
```

### Example

Fetch the name of a single extension:
```sh
python chrome-extension-to-name.py aaaaaaaaaaaaaaaabbbbbbbbbbbbbb
```

Fetch names from a file and export to CSV:
```sh
python chrome-extension-to-name.py -f extensions.txt --csv output.csv
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## Contact

For any questions or suggestions, please open an issue on GitHub.
