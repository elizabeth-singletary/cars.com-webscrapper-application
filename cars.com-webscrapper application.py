from operator import contains
from pickle import TRUE
from venv import create
from bs4 import BeautifulSoup
from openpyxl import Workbook
import requests
import pandas as pd
import re


# Find Number of Possible Pages
def findPages(soup: BeautifulSoup):
    totaMatches = soup.find(class_='total-entries').string.split(" ")[0]
    numMatches = int(totaMatches.replace(",",""))
    numpage = numMatches//20 - 1
    return numpage

# Create Initial Dataframe
def main():
    starturl = f"https://www.cars.com/shopping/results/?page=1&page_size=20&body_style_slugs[]=suv&dealer_id=&keyword=&list_price_max=35000&list_price_min=&makes[]=&maximum_distance=75&mileage_max=50000&sort=best_match_desc&stock_type=used&year_max=&year_min=2020&zip=27514"
    res = requests.get(starturl)
    soup = BeautifulSoup(res.text, 'lxml')
    numpage = findPages(soup)
    names = []
    prices = []
    years = []
    mileage = []
    link = []
    dealership = []
    for i in range(1,2):  #Replace with numpages later
        urlnew = starturl.replace(f"?page=1",f"?page={i}")
        res = requests.get(urlnew)
        soup = BeautifulSoup(res.text, 'lxml')
        vehicledet = soup.find_all(class_='vehicle-card')
        for vehicle in vehicledet:
            vehicle_name = str(vehicle.find(class_='title').string)
            names.append(vehicle_name)
            year = re.findall(r'\d\d\d\d',str(vehicle_name))
            years.append(int(year[0]))
            vehicle_price = str(vehicle.find(class_='primary-price').string).replace('$','').replace(',','')
            prices.append(vehicle_price)
            vehicle_mileage = vehicle.find(class_='mileage')
            try:
                strvehicle = int(str(vehicle_mileage.string).replace(',','').replace('mi.',''))
                mileage.append(strvehicle)
            except:
                mileage.append("n/a")

            vehicle_link = vehicle.find('a')
            link.append((f"cars.com{vehicle_link['href']}"))
            try:
                vehicle_dealership = str(vehicle.find(class_="dealer-name").contents[1].string)
                dealership.append(vehicle_dealership)
            except: 
                dealership.append("n/a")
            urlnew = starturl
           
    data = {"Names": names, "Prices": prices, "Year": years, "Mileage": mileage, "Dealership": dealership, "Link": link }
    df = pd.DataFrame(data)
    fdf = df.loc[:, df.columns!='Link']
    export = input("Would you like to export document(yes/no)? ").lower()
    if export == 'yes':
        df.to_excel('writer.xlsx')
        print("export succesful")

    return None

# Filter for Removal
def FilterBrandRemove(df: pd.DataFrame):
    brand = input("What dealership would you like to remove: ")
    filtecho = df['Dealership'].str.contains(brand, case=False)
    df = df[~filtecho]
    
    return df



# Find only Unique Brands
def FilterUniqueBrands(df: pd.DataFrame):
    brandDict = {}
    brandList = []
    for car in df["Names"]:
        if car in brandDict:
            continue
        else: 
            brandDict[car] = car
            brandList.append(car)
    return brandList

main()




