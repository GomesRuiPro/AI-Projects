#!/usr/bin/env python3
import os
import argparse
import sys
from innovation.FeedbackerAi.tools.local.utilities import Utility
from enum import Enum
import requests
from bs4 import BeautifulSoup
import json
from typing import Optional, Dict, Any

BROWSER = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'

# This script has a very specific way of working:
# 1. Input arguments need to follow a specific order: id,name,class,type to apply the filter. All of them are optional but at least 1 needs to be provided
# 2. There are 2 filters available: parent and child. The parent is optional and if none, the child should be like a table if you expect to get multiple values. 
# If parent is used, then mark the above element of the multiple children html elements that should share the same configuration: label, id, ... 
# 3. You can also use custom ui attributes, by specifying custom_label=test at the end of the list of the filter
# 4. If you want to get the data from an element attribute, specify the field attr_to_fetch. Otherwise, attr_to_fetch=value will be used instead, to which will get the value of that element.
# E.g.: <span>value</span>

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

def extract_attr_data(attr_elements, field, max_results=1):

    attr_data = []
    if len(attr_elements) > max_results:
        attr_elements = attr_elements[:max_results+1]
        
    for attr_element in attr_elements:
        attr_data.append(attr_element[field])

    return [{field: attr_data}]

def extract_value_data(attr_elements, field, max_results=1):

    attr_data = []
    if len(attr_elements) > max_results:
        attr_elements = attr_elements[:max_results+1]
        
    for attr_element in attr_elements:
        attr_element.find(field).text
        attr_data.append(attr_element.find(field).text)

    return [{field: attr_data}]

def __build_args(ui_component):
    ui_component_list = ui_component.split(',') 
      
    attrs = {}
    for index, attr in enumerate(ui_component_list):
        if attr:
            if index == 0:
                attrs["id"] = attr
            elif index == 1:
                attrs["name"] = attr
            elif index == 2:
                attrs["class"] = attr
            elif index == 3:
                attrs["type"] = attr
            else:
                attrs[Utility.substring_until_char(attr, "=")] = Utility.substring_from_char(attr, "=")
    return attrs

def extract_html_list(element, ui_component):
    soup = BeautifulSoup(str(element), 'html.parser')  
    attrs = __build_args(ui_component)
    return soup.find_all(attrs=attrs)

def extract_html_single(element, ui_component):
    soup = BeautifulSoup(str(element), 'html.parser')  
    attrs = __build_args(ui_component)
    return soup.find(attrs=attrs)
    
def scrapping(url, attr_to_fetch, type_to_fetch, filter, parent_filter="", max_results=1):

    headers = {
        'User-Agent': BROWSER
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
       
        element = None
        if parent_filter:
            parent_element = extract_html_single(response.text, parent_filter)
            if not parent_element:
                raise SubprocessError(f"No html element found!")
            element = extract_html_list(parent_element, filter)
        else:
            element = extract_html_single(response.text, filter)
            
        if not element:
            raise SubprocessError(f"No html element found!")
        
        html_data = None
        if type_to_fetch == 'table':
            html_data = extract_table_data(element, max_results)
        elif not attr_to_fetch == 'value':
            html_data = extract_attr_data(element, attr_to_fetch, max_results)
        else:
            html_data = extract_value_data(element, type_to_fetch, max_results)
        if not html_data:
            raise SubprocessError(f"No html data found!")
        
        return json.dumps(html_data)

    else:
        raise SubprocessError(f"Failed to access url with code {response.status_code}")


def main():
    parser = argparse.ArgumentParser(description='Web Scrapper Tool')
    parser.add_argument('domain', type=str, help='web domain')
    parser.add_argument('resource', type=str, help='path to resource')
    parser.add_argument('--type_to_fetch', type=str, help='UI class type to look for')
    parser.add_argument('--attr_to_fetch', type=str, default='value', help='UI attribute to look for')
    parser.add_argument('--filter', type=str, help='UI child id,name,class,type to look for')
    parser.add_argument('--parent_filter', type=str, default="", help='UI parent id,name,class,type to look for')
    parser.add_argument('--max_results', type=int, default=1, help='Maximum number of results to fetch')
    # parser.add_argument('--cache_enabled', action='store_true', help='To enable caching the results into a text file')
    # parser.add_argument('--memento_enabled', action='store_true', help='To enable historical data in cache')

    args = parser.parse_args()
    url = f"https://www.{args.domain}/{args.resource}/"
    
    # if args.memento_enabled and not args.cache_enabled:
    #     print("Error: --memento_enabled cannot be used without --cache_enabled", file=sys.stderr)
    #     sys.exit(1)
    
    try: 
        
        # main_topic = Utility.substring_until_char(args.domain, ".")
        # sub_topic = args.resource.replace("/", "_")
        # topic = f"{main_topic}_{sub_topic}"
        
        results = ""
        method_args = (url, args.attr_to_fetch, args.type_to_fetch, args.filter, args.parent_filter, args.max_results)
        # if args.cache_enabled:
        #     results = CacheClient.caching(topic, scrapping, method_args, args.memento_enabled)
        # else:
        #     results = scrapping(*method_args)
        results = scrapping(*method_args)                
        if not results:
            raise SubprocessError("No results found!")
            
        # results_str = Utility.list_of_dict_to_str(results)
        
        # if args.cache_enabled:
        #     topic = f"{args.domain}_{args.resource}"
        #     caching(topic, results_str, args.memento_enabled)
        # else:
        #     print(results_str)
            
    except Exception as ex:
        print(f"An error occurred for web scrapping in {url}: {ex}", file=sys.stderr)
        sys.exit(1)

    print(results)
    sys.exit(0)


if __name__ == "__main__":
    main()
