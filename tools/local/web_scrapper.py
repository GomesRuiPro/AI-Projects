#!/usr/bin/env python3
import os
import argparse
import sys
from innovation.FeedbackerAi.tools.utilities import Utility
from enum import Enum
import requests
from bs4 import BeautifulSoup
from memory.cache import CacheClient

BROWSER = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'

class TimeoutExpired(Exception):
    pass

class SubprocessError(Exception):
    pass
        
def extract_table_data(table_element, max_rows=1):
    # Get header columns
    headers = []
    header_row = table_element.find('tr')
    if header_row:
        for th in header_row.find_all(['th', 'td']):
            headers.append(th.text.strip())

    # Get all data rows (skip header)
    data_rows = table_element.find_all('tr')[1:max_rows+1]
    table_data = []

    for row in data_rows:
        cells = row.find_all('td')
        row_data = {}
        for idx, cell in enumerate(cells):
            # Use header names as keys if available
            key = headers[idx] if idx < len(headers) else f'Column_{idx+1}'
            row_data[key] = cell.text.strip()
        table_data.append(row_data)

    return table_data
        
def scrapping(url, ui_type, ui_id, max_results=1):

    headers = {
        'User-Agent': BROWSER
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        element = soup.find(ui_type, id=ui_id)
        
        if ui_type == 'table':
            return Utility.list_of_dict_to_str(extract_table_data(element, max_results))

    else:
        raise SubprocessError(f"Failed to access url with code {response.status_code}")
    return ""


def main():
    parser = argparse.ArgumentParser(description='Web Scrapper Tool')
    parser.add_argument('domain', type=str, help='web domain')
    parser.add_argument('resource', type=str, help='path to resource')
    parser.add_argument('ui_type', type=str, help='UI class type to look for')
    parser.add_argument('ui_id', type=str, help='UI id to look for')
    parser.add_argument('--cache_enabled', action='store_true', help='To enable caching the results into a text file')
    parser.add_argument('--memento_enabled', action='store_true', help='To enable historical data in cache')
    parser.add_argument('--max_results', type=int, default=1,
                        help='Maximum number of results to fetch')

    args = parser.parse_args()
    
    if args.memento_enabled and not args.cache_enabled:
        print("Error: --memento_enabled cannot be used without --cache_enabled")
        sys.exit(1)
    
    url = f"https://{args.domain}.com/{args.resource}"
    try: 
        
        topic = f"{args.domain}_{args.resource}"
        
        results = ""
        if args.cache_enabled:
            results = CacheClient.caching(topic, scrapping, (url, args.ui_type, args.ui_id, args.max_results), args.memento_enabled)
        else:
            results = scrapping(url, args.ui_type, args.ui_id, args.max_results)
            print(results)
                
        if not results:
            raise SubprocessError("No results found!")
            
        # results_str = Utility.list_of_dict_to_str(results)
        
        # if args.cache_enabled:
        #     topic = f"{args.domain}_{args.resource}"
        #     caching(topic, results_str, args.memento_enabled)
        # else:
        #     print(results_str)
            
    except Exception as ex:
        print(f"An error occurred for web scrapping in {url}: {ex}")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
