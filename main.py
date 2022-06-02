import time
import pyrebase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Config values for connecting Firebase Database
firebaseConfig = {
    "apiKey": "AIzaSyDxGVOZRbzh-Xa6i98dHL9z4JIq9xuBcwI",
    "authDomain": "testing-c6fdd.firebaseapp.com",
    "databaseURL": "https://testing-c6fdd-default-rtdb.firebaseio.com",
    "projectId": "testing-c6fdd",
    "storageBucket": "testing-c6fdd.appspot.com",
    "messagingSenderId": "444005072683",
    "appId": "1:444005072683:web:3ee2ee84ea4d29d9f18f6e",
    "measurementId": "G-PN5L5DF8TH"
}

# Initializing the Database
firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

# Creating dummy bank account with given parameters and uploading it to the database
data = {"TL_Balance": 100000, "Dollar_Balance": 0, "Euro_Balance": 0, "Gold_Balance": 0,
        "Total_Balance(TR)": 100000}
db.child("Account").set(data)

# Creating webdriver with given options
options = Options()
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(options=options)
driver.get("https://www.döviz.com/")

# Xpath for prices of Dollar, Euro and Gold
dollarBuyPriceXpath = "/html/body/main/div/div/div/table/tbody/tr[1]/td[3]"
dollarSellPriceXpath = "/html/body/main/div/div/div/table/tbody/tr[1]/td[4]"

EuroBuyPriceXpath = "/html/body/main/div/div/div/table/tbody/tr[2]/td[3]"
EuroSellPriceXpath = "/html/body/main/div/div/div/table/tbody/tr[2]/td[4]"

GoldBuyPriceXpath = "/html/body/main/div/div/div/table/tbody/tr[3]/td[3]"
GoldSellPriceXpath = "/html/body/main/div/div/div/table/tbody/tr[3]/td[4]"

# Putting Xpath's to a list so we can scan data using for loop
pricePaths = [dollarBuyPriceXpath, dollarSellPriceXpath, EuroBuyPriceXpath, EuroSellPriceXpath, GoldBuyPriceXpath,
              GoldSellPriceXpath]

# Creating two empty lists for storing current and previous prices of exchanges
previousPrices = []
currentPrices = []


# Function to get all of the values from website with given Xpath's
def get_prices():
    # Because we will keep updating prices, we need to clear the list before initialization
    currentPrices.clear()
    for i in pricePaths:
        currentPrices.append(driver.find_element(by=By.XPATH, value=i).text)


# Getting previous prices (which is required only at first iteration)
for i in pricePaths:
    previousPrices.append(driver.find_element(by=By.XPATH, value=i).text)


def dollarAccountCheck():
    if (currentPrices[0] < (previousPrices[0] - previousPrices[0] / 100)) and (balances["TL_Balance"] > 1000):
        balances["TL_Balance"] = balances["TL_Balance"] - 10 * currentPrices[0]
        balances["Dollar_Balance"] = balances["Dollar_Balance"] + 10
        print("Bought 10 Dollar for: ", currentPrices[0], " each.")
    if currentPrices[1] > (previousPrices[1] + previousPrices[1] / 200) and (balances["Dollar_Balance"] >= 5):
        balances["TL_Balance"] = balances["TL_Balance"] + 5 * currentPrices[1]
        balances["Dollar_Balance"] = balances["Dollar_Balance"] - 5
        print("Sold 5 Dollar for: ", currentPrices[1], " each.")


def euroAccountCheck():
    if (currentPrices[2] < (previousPrices[2] - previousPrices[2] / 100)) and (balances["TL_Balance"] > 1000):
        balances["TL_Balance"] = balances["TL_Balance"] - 10 * currentPrices[2]
        balances["Euro_Balance"] = balances["Euro_Balance"] + 10
        print("Bought 10 Euro for: ", currentPrices[2], " each.")
    if currentPrices[3] > (previousPrices[3] + previousPrices[3] / 200) and (balances["Euro_Balance"] >= 5):
        balances["TL_Balance"] = balances["TL_Balance"] + 5 * currentPrices[3]
        balances["Euro_Balance"] = balances["Euro_Balance"] - 5
        print("Sold 5 Euro for: ", currentPrices[3], " each.")


def goldAccountCheck():
    if (currentPrices[4] < (previousPrices[4] - previousPrices[4] / 100)) and (balances["TL_Balance"] > 1000):
        balances["TL_Balance"] = balances["TL_Balance"] - 10 * currentPrices[4]
        balances["Gold_Balance"] = balances["Gold_Balance"] + 10
        print("Bought 10 Gold for: ", currentPrices[4], " each.")
    if currentPrices[5] > (previousPrices[5] + previousPrices[5] / 200) and (balances["Gold_Balance"] >= 5):
        balances["TL_Balance"] = balances["TL_Balance"] + 5 * currentPrices[5]
        balances["Gold_Balance"] = balances["Gold_Balance"] - 5
        print("Sold 5 Gold for: ", currentPrices[5], " each.")


def calculateTotalBalance():
    # Calculating Total TR balance with new exchange rates according bought or sold units
    balances["Total_Balance(TR)"] = balances["TL_Balance"] + balances["Dollar_Balance"] * currentPrices[0] + balances[
        "Euro_Balance"] * currentPrices[2] + balances["Gold_Balance"] * currentPrices[4]
    # Update bank account (database)
    db.child("Account").set(balances)
    print(balances)


# Main loop that checks prices every hour and buys or sells according to price changes.
# Then updates the bank account (database) with current exchange prices and completed transactions
# timeCheck is for keeping track of the number of loops
timeCheck = 0
while True:
    timeCheck += 1
    # Refresh the page before executing commands (comment this while testing)
    # driver.refresh()

    # Get current exchange rates
    get_prices()

    # Convert string values to float in each list
    currentPrices = [float(i) for i in currentPrices]
    previousPrices = [float(i) for i in previousPrices]

    # Dictionary to get and store account details from database
    balances = {
        "TL_Balance": db.child("Account").get().val()["TL_Balance"],
        "Dollar_Balance": db.child("Account").get().val()["Dollar_Balance"],
        "Euro_Balance": db.child("Account").get().val()["Euro_Balance"],
        "Gold_Balance": db.child("Account").get().val()["Gold_Balance"],
        "Total_Balance(TR)": db.child("Account").get().val()["Total_Balance(TR)"]
    }

    # Buy 10 Unit (Dollar, Euro or Gold) if buying price is %1 lower than the previous noted rate
    # ...and the Turkish lira account has more than 1000 TLs
    # -----------------------------------------------------------------------------------------------
    # Sell 5 Unit (Dollar, Euro or Gold) if selling price is %0.5 higher than the previous noted rate
    # ...and the Unit account has more than or equal to 5 dollars
    # -----------------------------------------------------------------------------------------------
    # Than update account balances according to current exchange rates and completed transactions

    # For Dollar Account
    dollarAccountCheck()
    # For Euro Account
    euroAccountCheck()
    # For Gold Account
    goldAccountCheck()

    # Calculating Total TR balance with new exchange rates according bought or sold units
    # ... and update the bank account (database)
    calculateTotalBalance()

    # Update previous price list
    previousPrices = currentPrices.copy()

    # Wait for 1 hour (3600 seconds)
    time.sleep(5)

    # If loop has run 24 times
    if timeCheck == 24:
        break

# If  balance is more than 100.000 TLs, than print out “YOU WIN!”, else print out “YOU’RE LOSER!”
if balances["Total_Balance(TR)"] > 100000:
    print("YOU WIN!")
else:
    print("YOU’RE LOSER!")
