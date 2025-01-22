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

# Disable warnings for insecure requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_extension_name_from_id(extension_id, proxy):
    """
    Fetch the name of a Chrome extension using its ID.
    
    Args:
        extension_id (str): The ID of the Chrome extension.
        proxy (str): The proxy server to use for the request.
    
    Returns:
        str: The name of the Chrome extension.
    
    Raises:
        Exception: If the request fails or the extension name is not found.
    """
    url = f"https://chromewebstore.google.com/detail/{extension_id}"
    proxies = {
        "http": proxy,
        "https": proxy,
    }
    response = requests.get(url, proxies=proxies, verify=False)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch the URL: {url}")
    
    soup = BeautifulSoup(response.content, 'html.parser')
    h1_tag = soup.find('h1')
    if h1_tag:
        return h1_tag.text.strip()
    else:
        raise Exception("Extension name not found")

async def fetch_extension_name(session, extension_id, proxy):
    """
    Asynchronously fetch the name of a Chrome extension using its ID.
    
    Args:
        session (aiohttp.ClientSession): The aiohttp session to use for the request.
        extension_id (str): The ID of the Chrome extension.
        proxy (str): The proxy server to use for the request.
    
    Returns:
        tuple: A tuple containing the extension ID and its name or an error message.
    """
    url = f"https://chromewebstore.google.com/detail/{extension_id}"
    try:
        async with session.get(url, proxy=proxy, ssl=False) as response:
            if response.status != 200:
                return extension_id, f"Failed to fetch the URL: {url}"
            content = await response.text()
            soup = BeautifulSoup(content, 'html.parser')
            h1_tag = soup.find('h1')
            if h1_tag:
                return extension_id, h1_tag.text.strip()
            else:
                return extension_id, "Extension name not found"
    except Exception as e:
        return extension_id, str(e)

async def get_extension_names_from_file(file_path, proxy):
    """
    Asynchronously fetch the names of multiple Chrome extensions from a file containing their IDs.
    
    Args:
        file_path (str): The path to the file containing extension IDs.
        proxy (str): The proxy server to use for the requests.
    
    Returns:
        dict: A dictionary mapping extension IDs to their names or error messages.
    """
    with open(file_path, 'r') as file:
        extension_ids = file.read().splitlines()
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_extension_name(session, extension_id, proxy) for extension_id in extension_ids]
        results = await asyncio.gather(*tasks)
    
    return dict(results)

def export_to_csv(data, output_file):
    """
    Export the data to a CSV file.
    
    Args:
        data (dict): The data to export.
        output_file (str): The path to the output CSV file.
    """
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Extension ID', 'Extension Name'])
        for extension_id, extension_name in data.items():
            writer.writerow([extension_id, extension_name])

def export_to_excel(data, output_file):
    """
    Export the data to an Excel file with autofilter.
    
    Args:
        data (dict): The data to export.
        output_file (str): The path to the output Excel file.
    """
    df = pd.DataFrame(list(data.items()), columns=['Extension ID', 'Extension Name'])
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Extensions')
        worksheet = writer.sheets['Extensions']
        worksheet.autofilter(0, 0, df.shape[0], df.shape[1] - 1)

def export_to_json(data, output_file):
    """
    Export the data to a JSON file.
    
    Args:
        data (dict): The data to export.
        output_file (str): The path to the output JSON file.
    """
    with open(output_file, 'w') as jsonfile:
        json.dump(data, jsonfile, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get Chrome extension name from its ID")
    parser.add_argument("extension_id", nargs='?', help="The ID of the Chrome extension")
    parser.add_argument("-p", "--proxy", help="Proxy server to use")
    parser.add_argument("-f", "--file", help="File containing list of extension IDs")
    parser.add_argument("--csv", help="Output CSV file")
    parser.add_argument("--excel", help="Output Excel file")
    parser.add_argument("--json", help="Output JSON file")
    args = parser.parse_args()
    
    if args.file:
        try:
            extension_names = asyncio.run(get_extension_names_from_file(args.file, args.proxy))
            if args.csv:
                export_to_csv(extension_names, args.csv)
            if args.excel:
                export_to_excel(extension_names, args.excel)
            if args.json:
                export_to_json(extension_names, args.json)
            for extension_id, extension_name in extension_names.items():
                print(f"{extension_id}: {extension_name}")
        except Exception as e:
            print(e)
            sys.exit(1)
    elif args.extension_id:
        try:
            extension_name = get_extension_name_from_id(args.extension_id, args.proxy)
            print(extension_name)
        except Exception as e:
            print(e)
            sys.exit(1)
    else:
        print("Please provide either an extension ID or a file containing extension IDs.")
        sys.exit(1)
