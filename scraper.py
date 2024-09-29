import argparse
from bs4 import BeautifulSoup as BS
import csv
import re
import requests
from tabulate import tabulate
import sys


# Web scraper software that finds tables on web-pages.
# Run "python scraper.py -h" for help
def main():
    # Parsing arguments from the command line
    parser = argparse.ArgumentParser(
        description="Program that finds tables at html pages, and then prints them on the screen or returns a csv file"
    )
    parser.add_argument(
        "-n",
        "--number",
        default=0,
        help="Finds a table at the nth location on the page. Default value: 0",
        type=int,
    )
    parser.add_argument(
        "-c",
        "--csv",
        help="Outputs a csv file of the table if a table is found. Default value: false",
        action="store_true",
    )
    parser.add_argument(
        "-s",
        "--silent",
        help="Does not print a table or any other information to the command line. Default value: false",
        action="store_true",
    )
    parser.add_argument(
        "-a",
        "--all",
        help="Prints all tables on the page from the nth position onwards. Default value: false",
        action="store_true",
    )
    parser.add_argument(
        "-f",
        "--force",
        help="Prints entire rows of the table, even if there is no <td> tag. Default value: false",
        action="store_true",
    )
    args = parser.parse_args()

    # Gets input from the user
    if args.silent != True:
        print('HTML table parser. Run "python scraper.py -h" for help')
    url = input("Enter Url: ")
    n = args.number
    f = args.force
    while True:
        # Gets the nth html table from a specified url
        table = get_html_table(url, n, f)

        # Executes actions according to the arguments provided in the command line
        # Silences printing a table if in silent mode
        if args.silent != True:
            print(tabulate(table, headers="keys", tablefmt="outline"))

        # Outputs a CSV file if in CSV mode
        if args.csv == True:
            with open(f"table_{n+1}.csv", "w", encoding="utf-8", newline="") as f:
                # Sets fieldnames and writes the csv files
                fieldnames = [key for key in table[0].keys()]
                if len(table) > 1:
                    if len(fieldnames) < len([key for key in table[1].keys()]):
                        fieldnames = [key for key in table[1].keys()]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for row in table:
                    writer.writerow(row)
        if args.all == False:
            break
        n += 1

    sys.exit(0)


# Scraping the url and gets the first table in that page
def get_html_table(url_: str, location: int = 0, force=False):

    # Gets the raw html table
    try:
        response = requests.get(url_)
    except requests.exceptions.MissingSchema:
        print("Invalid url.")
        return sys.exit(1)

    soup = BS(response.text, "html.parser")
    try:
        html_table = soup.find_all("table")[location]
    except IndexError:
        print("No table was found at the specified location.")
        return sys.exit(1)

    # Attempts to create table titles if not in forced mode
    table_titles = []
    if force != True:
        table_titles_raw = html_table.find_all("th")
        table_titles = [title.text.strip() for title in table_titles_raw]

    if len(table_titles) < 1:
        force = True

    # Gets the data from the table
    final_table_data = []
    table_rows = html_table.find_all("tr")

    for row in table_rows:
        if force != True:
            table_data_raw = row.find_all("td")
        else:
            table_data_raw = row.find_all(re.compile(r"^t\w"))
        table_data = [data.text.strip() for data in table_data_raw]
        final_table_data.append(table_data)

    # Creates table titles in forced mode
    if force == True:
        table_titles = final_table_data.pop(0)

    # Creates a final table as a list of dictionaries
    final_table = []
    for row in final_table_data:
        if len(row) == 0:
            continue
        tmp = dict()
        for i, data in enumerate(row):
            tmp[table_titles[i]] = data

        final_table.append(tmp)

    return final_table


if __name__ == "__main__":
    main()
