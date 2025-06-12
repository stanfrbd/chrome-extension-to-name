import requests
from bs4 import BeautifulSoup
import argparse
import urllib3
import sys
import aiohttp
import asyncio
import csv
import pandas as pd
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_extension_name_from_id(extension_id, proxy, browser=None):
    """
    Fetch the name of a Chrome or Edge extension using its ID.
    """
    urls = []
    if browser == "chrome" or browser is None:
        urls.append(("Chrome", f"https://chromewebstore.google.com/detail/{extension_id}"))
    if browser == "edge" or browser is None:
        urls.append(("Edge", f"https://microsoftedge.microsoft.com/addons/detail/{extension_id}"))

    proxies = {"http": proxy, "https": proxy} if proxy else None

    for browser_name, url in urls:
        try:
            response = requests.get(url, proxies=proxies, verify=False, timeout=10)
            if response.status_code != 200:
                continue
            soup = BeautifulSoup(response.content, "html.parser")
            if browser_name == "Edge":
                title_tag = soup.find("title")
                if title_tag:
                    name = title_tag.text.strip().split("-")[0].strip()
                    return name, browser_name
            else:
                h1_tag = soup.find("h1")
                if h1_tag:
                    return h1_tag.text.strip(), browser_name
        except Exception:
            continue
    raise Exception("Extension name not found")


async def fetch_extension_name(session, extension_id, proxy, browser=None):
    """
    Asynchronously fetch the name of a Chrome or Edge extension using its ID.
    """
    urls = []
    if browser == "chrome" or browser is None:
        urls.append(("Chrome", f"https://chromewebstore.google.com/detail/{extension_id}"))
    if browser == "edge" or browser is None:
        urls.append(("Edge", f"https://microsoftedge.microsoft.com/addons/detail/{extension_id}"))

    for browser_name, url in urls:
        try:
            async with session.get(url, proxy=proxy, ssl=False, timeout=10) as response:
                if response.status != 200:
                    continue
                content = await response.text()
                soup = BeautifulSoup(content, "html.parser")
                if browser_name == "Edge":
                    title_tag = soup.find("title")
                    if title_tag:
                        name = title_tag.text.strip().split("-")[0].strip()
                        return extension_id, name, browser_name
                else:
                    h1_tag = soup.find("h1")
                    if h1_tag:
                        return extension_id, h1_tag.text.strip(), browser_name
        except Exception:
            continue
    return extension_id, "Extension name not found", ""


async def get_extension_names_from_file(file_path, proxy, browser=None):
    with open(file_path, "r") as file:
        extension_ids = file.read().splitlines()
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_extension_name(session, extension_id, proxy, browser) for extension_id in extension_ids]
        results = await asyncio.gather(*tasks)
    # Build dictionary: key = extension_id, value = (name, browser)
    return {extension_id: (name, browser) for extension_id, name, browser in results}


def export_data(data, output_file, filetype):
    if filetype == "csv":
        with open(output_file, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Extension ID", "Extension Name", "Browser"])
            for extension_id, value in data.items():
                extension_name = value[0]
                browser = value[1] if len(value) > 1 else ""
                writer.writerow([extension_id, extension_name, browser])
    elif filetype == "excel":
        rows = [[extension_id, value[0], value[1] if len(value) > 1 else ""] for extension_id, value in data.items()]
        df = pd.DataFrame(rows, columns=["Extension ID", "Extension Name", "Browser"])
        with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Extensions")
            worksheet = writer.sheets["Extensions"]
            worksheet.autofilter(0, 0, df.shape[0], df.shape[1] - 1)
    elif filetype == "json":
        serializable_data = {
            k: {"Extension Name": v[0], "Browser": v[1] if len(v) > 1 else ""} for k, v in data.items()
        }
        with open(output_file, "w") as jsonfile:
            json.dump(serializable_data, jsonfile, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get Chrome or Edge extension name from its ID")
    parser.add_argument("extension_id", nargs="?", help="The ID of the extension")
    parser.add_argument("-p", "--proxy", help="Proxy server to use")
    parser.add_argument("-f", "--file", help="File containing list of extension IDs")
    parser.add_argument("--csv", help="Output CSV file")
    parser.add_argument("--excel", help="Output Excel file")
    parser.add_argument("--json", help="Output JSON file")
    parser.add_argument("--browser", choices=["chrome", "edge"], help="Browser extension store to use")
    args = parser.parse_args()

    extension_names = {}

    if args.file:
        try:
            extension_names = awaitable = asyncio.run(
                get_extension_names_from_file(args.file, args.proxy, args.browser)
            )
        except Exception as e:
            print(e)
            sys.exit(1)
    elif args.extension_id:
        try:
            name, browser = get_extension_name_from_id(args.extension_id, args.proxy, args.browser)
            extension_names[args.extension_id] = (name, browser)
        except Exception as e:
            print(e)
            sys.exit(1)
    else:
        print("Please provide either an extension ID or a file containing extension IDs.")
        sys.exit(1)

    # Export if requested
    if args.csv:
        export_data(extension_names, args.csv, "csv")
    if args.excel:
        export_data(extension_names, args.excel, "excel")
    if args.json:
        export_data(extension_names, args.json, "json")

    # Print results
    for extension_id, value in extension_names.items():
        extension_name = value[0]
        browser = value[1] if len(value) > 1 else ""
        print(f"{extension_id}: {extension_name} ({browser})")
