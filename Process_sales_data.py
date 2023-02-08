from sys import argv, exit
import os
from datetime import date
import pandas as pd
import re

CUSTOMER_NAME_PATTERN = r"^[\w\s,'.-]+$"

def main():
    sales_csv = get_sales_csv()
    order_dir = create_order_dir(sales_csv)
    process_sales_data(sales_csv, order_dir)

#Get Path of Sales Data Files CSV
def get_sales_csv():
    #practicing some defensive programming
    #trying to use guard rails
#Check command line parameter
    if len(argv) > 2:
        print(f"Too many arguments received") # or we can assume a mistake, parse out the filename anyways, ignore the rest. this would make things easier, and would be a nice surprise if it worked despite human error (extra args)
        return
    if len(argv) <= 1:
        print("ERROR: CSV file path has not been provided")
    sales_csv = argv[1]
        #Check Provider Parameter for valid Path
    print(f"Checking if {sales_csv} is a valid filename")
    if not os.path.isfile(sales_csv):
        print('Error: Invalid Path to sales data CSV file. It wasn\'t found')
        return
    if not sales_csv.endswith(".csv"):
        print("This does not have a .csv file extension buddy!!!")
        return
    print("valid csv so far")
    return sales_csv

def create_order_dir(sales_csv):
    #Get Directory in sales data CSV file resides
    sales_dir = os.path.dirname(os.path.abspath(sales_csv))
    #Determine path of the directory to hold order files
    todays_date = date.today().isoformat()
    orders_dir = os.path.join(sales_dir, f'Orders_{todays_date}')
    #Create other Directory if it exist
    if not os.path.isdir(orders_dir):
        os.makedirs(orders_dir)
    return orders_dir

def format_price(price):
    return "${:,.2f}".format(price)

#Split data into individual order and save it to Excel sheets
def process_sales_data(sales_csv, orders_dir):
    grouped_sales = pd.read_csv(sales_csv).groupby("ORDER ID") #Creating list of orders, primary key being the `order id`
    for order_id, orders in grouped_sales:
        new_df = pd.DataFrame(orders, columns=["ORDER DATE", "ITEM NUMBER", "PRODUCT LINE", "PRODUCT CODE", "ITEM QUANTITY", "ITEM PRICE", "STATUS", "CUSTOMER NAME"])
        new_df["TOTAL_PRICE"] = new_df["ITEM QUANTITY"] * new_df["ITEM PRICE"]
        grand_total = "${:,.2f}".format(new_df["TOTAL_PRICE"].sum())
        new_df.sort_values(by='ITEM NUMBER', ascending=True, inplace=True)
        new_df = new_df.append({"TOTAL_PRICE": grand_total}, ignore_index=True)
        export_order_to_excel(order_id, new_df, orders_dir)

#return
def export_order_to_excel(order_id, order_df, order_dir):
    # Determine File and Path of Order Excel sheet
    customer_name = order_df['CUSTOMER NAME'].values[0]
    print(customer_name)
    if re.search(CUSTOMER_NAME_PATTERN, customer_name):
            customer_name = re.sub(CUSTOMER_NAME_PATTERN, "", customer_name)
    order_file = f'order-{order_id}.xlsx'
    order_path = os.path.join(order_dir, order_file)
    sheet_name = f'order#{order_id}'
    order_df.to_excel(order_path, index=False, sheet_name=sheet_name)
#return
main()

