from functools import total_ordering
import tkinter
from tkinter import *
from tkinter import ttk
import sqlite3
from PIL import ImageTk, Image
from io import BytesIO



dbfilepath='./SQL_Project_script.db'

root = Tk()

userID=None
shoppingCart = list()

def newFrame(frame, frame2):
    for widget in frame.winfo_children():
        if isinstance(widget, tkinter.Entry):
            widget.delete(0, "end")
    dropCardErrorLabel.config(text='')
    addCardErrorLabel.config(text='')
    newAccountErrorLabel.config(text='')
    customerSignInErrorLabel.config(text='')
    changeInfoAccountErrorLabel.config(text='')
    checkOutErrorLabel.config(text='')
    shoppingCartErrorLabel.config(text='')
    frame.pack_forget()
    frame2.pack()


def newUser(first, middle, last, email, address):
    db = sqlite3.connect(dbfilepath)
    cursor = db.cursor()
    cursor.execute("select count(*) from Customer where email = '"+email+"'")
    emailresult = cursor.fetchone()
    if int(emailresult[0])>0:
        newAccountErrorLabel.config(text="There is already an account with that email")
        db.close()
        return
    if not first or not last or not email:
        newAccountErrorLabel.config(text="Please make sure to fill out all required elements")
    else:
        cursor.execute("insert into Customer values (null, '"+first+"', '"+middle+"', '"+last+"', 'no', '"+address+"', '"+email+"')")
        db.commit()
        cursor.execute("select u_id from Customer where email = '" + email + "'")
        uidNumber = cursor.fetchone()
        newAccountErrorLabel.config(text="Account made successfully! Your UID is "+ str(uidNumber[0]))
    db.close()

def signIn(email, uid):
    db = sqlite3.connect(dbfilepath)
    cursor=db.cursor()
    cursor.execute("select count(*) from Customer where email='"+email+"' and u_id='"+uid+"'")
    loginresult = cursor.fetchone()

    if int(loginresult[0])>0:
        customerSignInErrorLabel.config(text="")
        global userID
        userID=uid

        #for profile page
        cursor.execute("select first_name, middle_name, last_name, subscription_status from Customer where email='"+email+"' and u_id='"+uid+"'")
        nameResult = cursor.fetchone()
        greetingLabel.config(text="Hello, "+nameResult[0]+" "+nameResult[1]+" "+nameResult[2], font=('Helvetica Bold', 25))
        uidReminderLabel.config(text="UID: "+uid, font=('Helvetica Bold', 25))
        emailReminderLabel.config(text="EMAIL: "+email, font=('Helvetica Bold', 25))
        subscriptionLabel.config(text="Subscription: "+nameResult[3])
        viewSalesHistory()
        viewCards()
        viewTrackingOrders()

        #for main page
        signInButton.place_forget()
        logInButton.place(relx=.872)
        newFrame(customerSignInPage, profilePage)
    else:
        customerSignInErrorLabel.config(text="No account found with that information.")
    db.close()


def logOut():
    logInButton.place_forget()
    signInButton.place(relx=.872)
    global userID
    userID=None
    shoppingCartListBox.delete(0, shoppingCartListBox.size()-1)
    newFrame(profilePage, mainPage)


def changeSubscription():
    db = sqlite3.connect(dbfilepath)
    cursor = db.cursor()
    cursor.execute("select subscription_status from Customer where u_id='"+userID+"'")
    substatus=cursor.fetchone()
    if substatus[0]=="no":
        cursor.execute("update Customer set subscription_status = 'yes' where u_id='"+userID+"'")
        db.commit()
        subscriptionLabel.config(text="Subscription: yes" )
    else:
        cursor.execute("update Customer set subscription_status ='no' where u_id='" + userID + "'")
        db.commit()
        subscriptionLabel.config(text="Subscription: no")

    db.close()

def viewSalesHistory():
    db = sqlite3.connect(dbfilepath)
    cursor = db.cursor()
    cursor.execute("select * from view_sales_data where u_id = '"+userID+"'")
    sales_history = cursor.fetchall()
    tv = ttk.Treeview(salesHistoryPage, columns=(1,2,3,4,5,6,7,8), show="headings", height=9)
    tv.place(relx=.175, rely=.2)

    tv.column(1, anchor=CENTER, stretch=NO, width=60)
    tv.column(2, anchor=CENTER, stretch=NO, width=80)
    tv.column(3, anchor=CENTER, stretch=NO, width=110)
    tv.column(4, anchor=CENTER, stretch=NO, width=70)
    tv.column(5, anchor=CENTER, stretch=NO, width=80)
    tv.column(6, anchor=CENTER, stretch=NO, width=120)
    tv.column(7, anchor=CENTER, stretch=NO, width=80)
    tv.column(8, anchor=CENTER, stretch=NO, width=70)

    tv.heading(1, text='Order ID')
    tv.heading(2, text='Product ID')
    tv.heading(3, text='Product Name')
    tv.heading(4, text='Price($)')
    tv.heading(5, text='Brand')
    tv.heading(6, text='Purchase Time')
    tv.heading(7, text='Store Region')
    tv.heading(8, text='User ID')

    for i in sales_history:
        tv.insert('','end',values = i)

    SalesHistoryScrollbar = Scrollbar(salesHistoryPage, orient=VERTICAL)
    SalesHistoryScrollbar.config(command=tv.yview)
    SalesHistoryScrollbar.place(relx=.87, rely=.2, height=205)
    tv.config(yscrollcommand=SalesHistoryScrollbar.set)

    db.close()

def viewTrackingOrders():
    db = sqlite3.connect(dbfilepath)
    cursor = db.cursor()
    cursor.execute("select * from view_track_num where u_id = '"+userID+"'")
    trackingOrders = cursor.fetchall()

    tv = ttk.Treeview(trackingOrderPage, columns=(1, 2, 3, 4, 5, 6, 7), show="headings", height=9)
    tv.place(relx=.175, rely=.2)

    tv.column(1, anchor=CENTER, stretch=NO, width=65)
    tv.column(2, anchor=CENTER, stretch=NO, width=80)
    tv.column(3, anchor=CENTER, stretch=NO, width=150)
    tv.column(4, anchor=CENTER, stretch=NO, width=85)
    tv.column(5, anchor=CENTER, stretch=NO, width=80)
    tv.column(6, anchor=CENTER, stretch=NO, width=110)
    tv.column(7, anchor=CENTER, stretch=NO, width=80)

    tv.heading(1, text='Track ID')
    tv.heading(2, text='Shipper ID')
    tv.heading(3, text='Address')
    tv.heading(4, text='Product ID')
    tv.heading(5, text='Brand')
    tv.heading(6, text='Product Name')
    tv.heading(7, text='User ID')

    for i in trackingOrders:
        tv.insert('', 'end', values=i)

    trackingOrdersScrollbar = Scrollbar(trackingOrderPage, orient=VERTICAL)
    trackingOrdersScrollbar.config(command=tv.yview)
    trackingOrdersScrollbar.place(relx=.85, rely=.2, height=205)
    tv.config(yscrollcommand=trackingOrdersScrollbar.set)

    db.close()

def viewCards():
    db = sqlite3.connect(dbfilepath)
    cursor = db.cursor()
    cursor.execute("select * from Customer_Card where u_id ='"+userID+"'")
    cards = cursor.fetchall()

    tv = ttk.Treeview(cardPage, columns=(1, 2, 3, 4, 5), show="headings", height=9)
    tv.place(relx=.1, rely=.2)

    tv.column(1, anchor=CENTER, stretch=NO, width=100)
    tv.column(2, anchor=CENTER, stretch=NO, width=80)
    tv.column(3, anchor=CENTER, stretch=NO)
    tv.column(4, anchor=CENTER, stretch=NO)
    tv.column(5, anchor=CENTER, stretch=NO)

    tv.heading(1, text='User ID')
    tv.heading(2, text='Card Type')
    tv.heading(3, text='Card Number')
    tv.heading(4, text='Balance($)')
    tv.heading(5, text='Monthly Debt')

    for i in cards:
        tv.insert('', 'end', values=i)

    cardPageScrollbar = Scrollbar(cardPage, orient=VERTICAL)
    cardPageScrollbar.config(command=tv.yview)
    cardPageScrollbar.place(relx=.92, rely=.2, height=205)
    tv.config(yscrollcommand=cardPageScrollbar.set)

    db.close()


def addCard(cardNum, cardBal, cardType):
    if cardType=="Select Your Card Type":
        addCardErrorLabel.config(text="Please choose a card type")
        return
    db = sqlite3.connect(dbfilepath)
    cursor = db.cursor()
    cursor.execute("select count(*) from Customer_Card where card_number = '" + cardNum + "'")
    cardresult = cursor.fetchone()
    if int(cardresult[0]) > 0:
        addCardErrorLabel.config(text="There is already an account with that card")
        db.close()
        return
    if not cardNum or not cardBal:
        addCardErrorLabel.config(text="Please make sure to fill out all required elements")
    elif not cardNum.isdigit() or not cardBal.isdigit():
        addCardErrorLabel.config(text="Information not valid")
    else:
        cursor.execute(
            "insert into Customer_Card values ('"+userID+"', '"+cardType+"', '"+cardNum+"', '"+cardBal+"', 0)")
        db.commit()
        addCardErrorLabel.config(text="Card successfully added!")
    db.close()

def dropCard(cardNum):
    db = sqlite3.connect(dbfilepath)
    cursor = db.cursor()

    cursor.execute("select count(*) from Customer_Card where card_number='"+cardNum+"' and u_id='"+userID+"'")
    cardResult = cursor.fetchone()
    if int(cardResult[0]) > 0:
        cursor.execute("delete from Customer_Card where card_number='"+cardNum+"' and u_id='"+userID+"'")
        db.commit()
        dropCardErrorLabel.config(text="Drop Successful!")
    else:
        dropCardErrorLabel.config(text="Card not found")

def changeInfo(first, middle, last, email, address):
    db=sqlite3.connect(dbfilepath)
    cursor=db.cursor()
    if not first or not last or not email:
        changeInfoAccountErrorLabel.config(text="Please make sure to fill out all required elements")
    else:
        cursor.execute("update Customer set first_name ='"+first+"', middle_name='"+middle+"', last_name='"+last+"', email='"+email+"',address='"+address+"' where u_id='"+userID+"'")
        db.commit()
        changeInfoAccountErrorLabel.config(text="Update successful")
        greetingLabel.config(text="Hello, " + first + " " + middle + " " + last,
                             font=('Helvetica Bold', 25))
        emailReminderLabel.config(text="EMAIL: " + email, font=('Helvetica Bold', 25))
    db.close()

def addProductToCart(pid):
    global shoppingCartListBox
    if pid<0:
        db=sqlite3.connect(dbfilepath)
        cursor=db.cursor()
        cursor.execute("select count(*) from Product")
        productCount=cursor.fetchone()
        truePID = pid+1+productCount[0]
        cursor.execute("select p_name, brand, price from Product where p_id='"+str(truePID)+"'")
        productInfo = cursor.fetchone()
        shoppingCartListBox.insert(END, "Product ID: "+str(truePID)+", "+"Product Name: "+str(productInfo[0])+", Brand: "+str(productInfo[1])+", Price: $"+str(productInfo[2]))
        db.close()
    else:
        db = sqlite3.connect(dbfilepath)
        cursor = db.cursor()
        truePID = pid + 1
        cursor.execute("select p_name, brand, price from Product where p_id='" + str(truePID) + "'")
        productInfo = cursor.fetchone()
        shoppingCartListBox.insert(END, "Product ID: "+str(truePID)+", "+"Product Name: "+str(productInfo[0])+", Brand: "+str(productInfo[1])+", Price: $"+str(productInfo[2]))
        db.close()

def addProductToCart(pid):
    global shoppingCartListBox
    if pid<0:
        db=sqlite3.connect(dbfilepath)
        cursor=db.cursor()
        cursor.execute("select count(*) from Product")
        productCount=cursor.fetchone()
        truePID = pid+1+productCount[0]
        cursor.execute("select p_name, brand, price from Product where p_id='"+str(truePID)+"'")
        productInfo = cursor.fetchone()
        shoppingCartListBox.insert(END, "Product ID: "+str(truePID)+", "+"Product Name: "+str(productInfo[0])+", Brand: "+str(productInfo[1])+", Price: $"+str(productInfo[2]))
        db.close()
    else:
        db = sqlite3.connect(dbfilepath)
        cursor = db.cursor()
        truePID = pid + 1
        cursor.execute("select p_name, brand, price from Product where p_id='" + str(truePID) + "'")
        productInfo = cursor.fetchone()
        shoppingCartListBox.insert(END, "Product ID: "+str(truePID)+", "+"Product Name: "+str(productInfo[0])+", Brand: "+str(productInfo[1])+", Price: $"+str(productInfo[2]))
        db.close()
def deleteItems():
    shoppingCartListBox.delete(ANCHOR)

def checkOut():
    if not userID:
        shoppingCartErrorLabel.config(text="Please sign in first")
    elif not shoppingCartListBox.get(0,'end'):
        shoppingCartErrorLabel.config(text="Cart is empty")
    else:
        db=sqlite3.connect(dbfilepath)
        cursor=db.cursor()
        cursor.execute("select card_number from Customer_Card where u_id='"+userID+"'")
        tempCardMenu=list()
        tempCardMenu.append("Please select a card")
        global checkOutCreditMenu
        global creditMenuStringVar
        creditMenuStringVar.set("Please select a card")
        checkOutCreditMenu.destroy()
        for x in cursor.fetchall():
            tempCardMenu.append(x[0])

        checkOutCreditMenu= OptionMenu(checkOutPage, creditMenuStringVar, *tempCardMenu)
        checkOutCreditMenu.place(relx=.1)
        db.close()
        totalPrice=0
        for x in shoppingCartListBox.get(0, 'end'):
            totalPrice+=int(x[x.index('$')+1:])
        checkOutTotalPriceLabel.config(text='Total Price: $'+str(totalPrice))
        newFrame(shoppingCartPage, checkOutPage)

def addDealToCart():
    global dealListBox
    selectedDeals = dealListBox.get(ANCHOR)
    if not selectedDeals:
        return
    else:
        shoppingCartListBox.insert(END, selectedDeals)

def onlineCheckOut():
    if creditMenuStringVar.get()=="Please select a card" or tempWareHouseStringVar.get()=="Choose a shipper":
        checkOutErrorLabel.config(text='Please select all needed requirements')
        return
    db=sqlite3.connect(dbfilepath)
    cursor=db.cursor()
    cursor.execute("select subscription_status from Customer where u_id='"+userID+"'")
    substat=cursor.fetchone()
    totalPrice = int(checkOutTotalPriceLabel.cget("text")[checkOutTotalPriceLabel.cget("text").index('$') + 1:])

    if checkOutSubscriberStringVar.get()=="Purchase as subscriber":
        #adding to their monthly debt, subscribers get charged monthly
        if substat[0]!= "yes":
            checkOutErrorLabel.config(text='You are not actually a subscriber')
            db.close()
            return
        else:
            cartList=dict()

            for x in shoppingCartListBox.get(0, 'end'):
                y=x.split(" ")
                if y[0]=="Product":

                    productKey=y[2][:len(y[2])-1]
                    if productKey in cartList.keys():
                        cartList[productKey]+=1
                    else:
                        cartList[productKey]=1
                else:

                    deal_id=y[2][:len(y[2])-1]
                    print(deal_id)
                    cursor.execute("select p_id, Quantity from Deal_Product where d_id='"+str(deal_id)+"'")
                    for z in cursor.fetchall():
                        for i in range(z[1]):
                            if z[0] in cartList.keys():
                                cartList[z[0]]+=1
                            else:
                                cartList[z[0]]=1
            for x in cartList.keys():
                cursor.execute("select quantity from Warehouse where w_id='"+tempWareHouseStringVar.get()+"' and p_id='"+str(x)+"'")
                quantityOfProduct=cursor.fetchone()
                if cartList[x]>quantityOfProduct[0]:
                    checkOutErrorLabel.config("Out of stock")
                    db.close()
                    return
            for x in cartList.keys():
                cursor.execute("update Warehouse set quantity=quantity-'"+str(cartList[x])+"' where w_id='"+tempWareHouseStringVar.get()+"' and p_id='"+str(x)+"'")
                db.commit()
                cursor.execute("select address from Customer where u_id='" + str(userID) + "'")
                address = cursor.fetchone()
                cursor.execute(
                    "insert into Online_Sales values(NULL, '" + str(userID) + "', '" + tempWareHouseStringVar.get() + "', '" +
                    str(address[0]) + "', '"+str(x)+"')")
                db.commit()
            cursor.execute("update Customer_Card set monthly_debt=monthly_debt+'"+str(totalPrice)+"' where card_number='"+creditMenuStringVar.get()+"'")
            db.commit()
            db.close()
            checkOutErrorLabel.config(text="Purchase successful!")
    else:
        cursor.execute("select balance from customer_card where card_number='"+creditMenuStringVar.get()+"'")
        if totalPrice>cursor.fetchone()[0]:
            checkOutErrorLabel.config(text="You don't have enough funds")
            db.close()
            return
        cartList = dict()
        for x in shoppingCartListBox.get(0, 'end'):
            y = x.split(" ")
            if y[0] == "Product":
                productKey = y[2][:len(y[2]) - 1]
                if productKey in cartList.keys():
                    cartList[productKey] += 1
                else:
                    cartList[productKey] = 1
            else:
                deal_id = y[2][:len(y[2]) - 1]
                cursor.execute("select p_id, Quantity from Deal_Product where d_id='" + deal_id + "'")
                for z in cursor.fetchall():
                    for i in range(z[1]):
                        if z[0] in cartList.keys():
                            cartList[z[0]] += 1
                        else:
                            cartList[z[0]] = 1
        for x in cartList.keys():
            cursor.execute(
                "select quantity from Warehouse where w_id='" + tempWareHouseStringVar.get() + "' and p_id='" + str(
                    x) + "'")
            quantityOfProduct = cursor.fetchone()
            if cartList[x] > quantityOfProduct[0]:
                checkOutErrorLabel.config("Out of stock")
                db.close()
                return
        for x in cartList.keys():
            cursor.execute("update Warehouse set quantity=quantity-'" + str(
                cartList[x]) + "' where w_id='" + tempWareHouseStringVar.get() + "' and p_id='" + str(x) + "'")
            db.commit()
            cursor.execute("select address from Customer where u_id='" + str(userID) + "'")
            address = cursor.fetchone()
            cursor.execute(
                "insert into Online_Sales values(NULL, '" + str(userID) + "', '" + tempWareHouseStringVar.get() + "', '" +
                str(address[0]) + "', '" + str(x) + "')")
            db.commit()
        cursor.execute("update Customer_Card set balance=balance-'" + str(
            totalPrice) + "' where card_number='" + creditMenuStringVar.get() + "'")
        db.commit()
        db.close()
        checkOutErrorLabel.config(text="Purchase successful!")



def offlineCheckOut():
    if creditMenuStringVar.get() == "Please select a card" or tempStoreStringVar.get() == "Choose a store":
        checkOutErrorLabel.config(text='Please select all needed requirements')
        return
    db = sqlite3.connect(dbfilepath)
    cursor = db.cursor()
    cursor.execute("select subscription_status from Customer where u_id='" + userID + "'")
    substat = cursor.fetchone()
    totalPrice = int(checkOutTotalPriceLabel.cget("text")[checkOutTotalPriceLabel.cget("text").index('$') + 1:])

    if checkOutSubscriberStringVar.get() == "Purchase as subscriber":
        # adding to their monthly debt, subscribers get charged monthly
        if substat[0] != "yes":
            checkOutErrorLabel.config(text='You are not actually a subscriber')
            db.close()
            return
        else:
            cartList = dict()

            for x in shoppingCartListBox.get(0, 'end'):
                y = x.split(" ")
                if y[0] == "Product":

                    productKey = y[2][:len(y[2]) - 1]
                    if productKey in cartList.keys():
                        cartList[productKey] += 1
                    else:
                        cartList[productKey] = 1
                else:

                    deal_id = y[2][:len(y[2]) - 1]

                    cursor.execute("select p_id, Quantity from Deal_Product where d_id'" + deal_id + "'")
                    for z in cursor.fetchall():
                        for i in range(z[1]):
                            if z[0] in cartList.keys():
                                cartList[z[0]] += 1
                            else:
                                cartList[z[0]] = 1
            for x in cartList.keys():
                cursor.execute(
                    "select quantity from Store where s_id='" + tempStoreStringVar.get() + "' and p_id='" + str(
                        x) + "'")
                quantityOfProduct = cursor.fetchone()
                if cartList[x] > quantityOfProduct[0]:
                    checkOutErrorLabel.config(text="Out of stock")
                    #order restock by 20 from each warehouse if low
                    cursor.execute("select distinct w_id from Warehouse")
                    warehouses=cursor.fetchall()
                    for y in warehouses:
                        cursor.execute("select quantity from Warehouse where w_id='"+str(y[0])+"' and p_id='"+str(x)+"'")
                        quantity=cursor.fetchone()
                        if quantity[0]>=20:
                            cursor.execute("update Store set quantity=quantity+20 where s_id='"+tempStoreStringVar.get()+"' and p_id='"+str(x)+"'")
                            db.commit()
                            cursor.execute("update Warehouse set quantity=quantity-20 where w_id='"+str(y[0])+"' and p_id='"+str(x)+"'")
                            db.commit()
                            cursor.execute("insert into Restock values('"+str(y[0])+"', '"+tempStoreStringVar.get()+"', '"+str(x)+"', 20, 'finished', DATE('now'))")
                        else:
                            cursor.execute("insert into Restock values('" + str(y[
                                0]) + "', '" + tempStoreStringVar.get() + "', '" + str(x) + "', 20, pending, DATE('now'))")
                    db.close()
                    return
            for x in cartList.keys():
                cursor.execute("update Store set quantity=quantity-'" + str(
                    cartList[x]) + "' where s_id='" + tempStoreStringVar.get() + "' and p_id='" + str(x) + "'")
                db.commit()


                cursor.execute(
                    "insert into Sales_data values(NULL, DATE('now'), '"+str(x)+"', 'offline', '" + str(userID) + "')")
                db.commit()
            cursor.execute("update Customer_Card set monthly_debt=monthly_debt+'" + str(
                totalPrice) + "' where card_number='" + creditMenuStringVar.get() + "'")
            db.commit()
            db.close()
            checkOutErrorLabel.config(text="Purchase successful!")
    else:
        cursor.execute("select balance from customer_card where card_number='" + creditMenuStringVar.get() + "'")
        if totalPrice > cursor.fetchone()[0]:
            checkOutErrorLabel.config(text="You don't have enough funds")
            db.close()
            return
        cartList = dict()

        for x in shoppingCartListBox.get(0, 'end'):
            y = x.split(" ")
            if y[0] == "Product":

                productKey = y[2][:len(y[2]) - 1]
                if productKey in cartList.keys():
                    cartList[productKey] += 1
                else:
                    cartList[productKey] = 1
            else:

                deal_id = y[2][:len(y[2]) - 1]

                cursor.execute("select p_id, Quantity from Deal_Product where d_id'" + str(deal_id) + "'")
                for z in cursor.fetchall():
                    for i in range(z[1]):
                        if z[0] in cartList.keys():
                            cartList[z[0]] += 1
                        else:
                            cartList[z[0]] = 1
        for x in cartList.keys():
            cursor.execute(
                "select quantity from Store where s_id='" + tempStoreStringVar.get() + "' and p_id='" + str(
                    x) + "'")
            quantityOfProduct = cursor.fetchone()
            if cartList[x] > quantityOfProduct[0]:
                checkOutErrorLabel.config(text="Out of stock")
                # order restock by 20 from each warehouse if low
                cursor.execute("select distinct w_id from Warehouse")
                warehouses = cursor.fetchall()
                for y in warehouses:
                    cursor.execute("select quantity from Warehouse where w_id='" + str(y[0]) + "' and p_id='" + str(x) + "'")
                    quantity = cursor.fetchone()
                    if quantity[0] >= 20:
                        cursor.execute(
                            "update Store set quantity=quantity+20 where s_id='" + tempStoreStringVar.get() + "' and p_id='" + str(
                                x) + "'")
                        db.commit()
                        cursor.execute(
                            "update Warehouse set quantity=quantity-20 where w_id='" + str(y[0]) + "' and p_id='" + str(
                                x) + "'")
                        db.commit()
                        cursor.execute(
                            "insert into Restock values('" + str(y[0]) + "', '" + tempStoreStringVar.get() + "', '" + str(
                                x) + "', 20, 'finished', DATE('now'))")
                    else:
                        cursor.execute("insert into Restock values('" + str(y[0]) + "', '" + tempStoreStringVar.get() + "', '" + str(x) + "', 20, 'pending', DATE('now'))")
                db.close()
                return
        for x in cartList.keys():
            cursor.execute("update Store set quantity=quantity-'" + str(
                cartList[x]) + "' where s_id='" + tempStoreStringVar.get() + "' and p_id='" + str(x) + "'")
            db.commit()

            cursor.execute(
                "insert into Sales_data values(NULL, DATE('now'), '" + str(x) + "', 'offline', '" + str(userID) + "')")
            db.commit()
        cursor.execute("update Customer_Card set balance=balance-'" + str(
            totalPrice) + "' where card_number='" + creditMenuStringVar.get() + "'")
        db.commit()
        db.close()
        checkOutErrorLabel.config(text="Purchase successful!")



#initialization of frames
mainPage = Frame(root, height=800, width=1200)
mainPage.grid_propagate(0)

customerSignInPage = Frame(root, height=600, width=350)
customerSignInPage.grid_propagate(0)

newAccountPage = Frame(root, height=600, width=350)
newAccountPage.grid_propagate(0)

profilePage = Frame(root, height=800, width=1200)
profilePage.grid_propagate(0)

salesHistoryPage = Frame(root, height=800, width=950)
salesHistoryPage.grid_propagate(0)

trackingOrderPage = Frame(root, height=900, width=950)
trackingOrderPage.grid_propagate(0)

cardPage = Frame(root, height=900, width=950)
cardPage.grid_propagate(0)

newCardPage = Frame(root, height=500, width=250)
newCardPage.grid_propagate(0)

addCardPage = Frame(root, height=400, width=400)
addCardPage.grid_propagate(0)

dropCardPage = Frame(root, height=400, width=600)
dropCardPage.grid_propagate(0)

changeInfoPage = Frame(root, height=600, width=600)
changeInfoPage.grid_propagate(0)

shoppingCartPage = Frame(root, height=600, width=600)
shoppingCartPage.grid_propagate(0)

checkOutPage = Frame(root, height=600, width=600)
checkOutPage.grid_propagate(0)


#mainPage
mainPageLogo = Label(mainPage, text="WORST BUY!!!", font=('Lucida Handwriting', 55))
mainPageLogo.place(relx=.01)

signInButton = Button(mainPage, text="Sign In", command=lambda: newFrame(mainPage, customerSignInPage), width=9, font=('Helvetica Bold', 20))
signInButton.place(relx=.872)

logInButton = Button(mainPage, text="Go to Profile", command=lambda :newFrame(mainPage, profilePage), width=9, font=('Helvetica Bold', 20))

dealBar = Label(mainPage, text="DEALS OF THE DAY", width=52, background="yellow", font=('Helvetica Bold', 30), anchor="center")
dealBar.place(rely=.175)

productBar = Label(mainPage, text="PRODUCTS", width=52, background="blue", font=('Helvetica Bold', 30))
productBar.place(rely=.575)

productNameLabel = Label(mainPage, font=('Helvetica Bold', 20))
productNameLabel.place(rely=.700)

productBrandLabel = Label(mainPage, font=('Helvetica Bold', 20))
productBrandLabel.place(rely=.750)

productPriceLabel = Label(mainPage, font=('Helvetica Bold', 20))
productPriceLabel.place(rely=.800)

db=sqlite3.connect(dbfilepath)
cursor=db.cursor()

cursor.execute("select * from Product")
productList=cursor.fetchall()
images = list()
productInfo = list()

for x in productList:
    img_bytes = BytesIO(x[5])
    opened_image = Image.open(img_bytes)
    opened_image.thumbnail((400,200))
    img = ImageTk.PhotoImage(opened_image)
    images.append(img)
    productInfo.append([x[1], x[2], x[3]])

db.close()

pid = 0
imageLabel = Label(mainPage, image=images[pid])
productNameLabel.config(text=productList[pid][1])
productBrandLabel.config(text=productList[pid][3])
productPriceLabel.config(text="$"+str(productList[pid][2]))

imageLabel.place(rely = .639, relx = .34)

#product button
def previous():
    global pid
    pid = pid - 1
    try:
        imageLabel.config(image=images[pid])
        productNameLabel.config(text=productList[pid][1])
        productBrandLabel.config(text=productList[pid][3])
        productPriceLabel.config(text="$"+str(productList[pid][2]))
    except:
        pid = 0
        previous()

def next():
    global pid
    pid = pid + 1
    try:
        imageLabel.config(image=images[pid])
        productNameLabel.config(text=productList[pid][1])
        productBrandLabel.config(text=productList[pid][3])
        productPriceLabel.config(text="$"+str(productList[pid][2]))
    except:
        pid = -1
        next()

btn1 = Button(mainPage, text="Previous", bg='black', fg='gold', font=('ariel 15 bold'), relief=GROOVE, command=previous)
btn1.place(relx = .2, rely=.8)
btn2 = Button(mainPage, text="Next", width=8, bg='black', fg='gold', font=('ariel 15 bold'), relief=GROOVE, command=next)
btn2.place(relx = .9, rely=.8)

#deals
dealListBox = Listbox(mainPage, width=80)
dealListBox.place(relx=.3, rely=.25)

db = sqlite3.connect(dbfilepath)
cursor = db.cursor()
cursor.execute("select * from Deal_Name")
dealName = cursor.fetchall()

for x in dealName:
    dealListBox.insert(END, "Deal ID: "+str(x[0])+", Description:"+str(x[2])+", Price: $"+str(x[1]))

dealAddToCartButton = Button(mainPage, text="Add Selected to cart", command=lambda: addDealToCart())
dealAddToCartButton.place(relx=.3, rely=.5)

# dealNameScrollbar = Scrollbar(mainPage, orient=VERTICAL)
# dealNameScrollbar.config(command=tv1.yview)
# dealNameScrollbar.place(relx=.735, rely=.25, height=127)
# tv1.config(yscrollcommand=dealNameScrollbar.set)

db.close()


addtoCartButton = Button(mainPage, font=('Helvetica Bold', 20), text='Add to Cart', command=lambda:addProductToCart(pid))
addtoCartButton.place(rely=.850)

toShoppingCartButton = Button(mainPage, text="Shopping Cart", command= lambda: newFrame(mainPage,shoppingCartPage), width=12, font=('Helvetica Bold', 20))
toShoppingCartButton.place(relx=.7)

mainPage.pack()


#customerSignInPage
customerEmailLabel = Label(customerSignInPage, text="Customer Email", font=('Helvetica Bold', 15))
customerEmailLabel.place(relx=.295, rely=.05)

customerEmailEntry = Entry(customerSignInPage, width=25)
customerEmailEntry.place(relx=.28, rely=.1)

customerUserIDLabel = Label(customerSignInPage, text="Customer User ID", font=('Helvetica Bold', 15))
customerUserIDLabel.place(relx=.265, rely=.15)

customerUserIDEntry = Entry(customerSignInPage, width=25)
customerUserIDEntry.place(relx=.28, rely=.2)

customerSignInButton = Button(customerSignInPage, text="Sign In", command=lambda: signIn(customerEmailEntry.get(), customerUserIDEntry.get()), font=('Helvetica Bold', 15))
customerSignInButton.place(relx=.38, rely=.25)

customerSignUpButton = Button(customerSignInPage, text="Make a New Account", command=lambda:newFrame(customerSignInPage, newAccountPage), font=('Helvetica Bold', 15))
customerSignUpButton.place(relx=.20, rely=.32)

customerBackToMainButton = Button(customerSignInPage, text="Return Back to Front Page", command=lambda: newFrame(customerSignInPage, mainPage))
customerBackToMainButton.place(relx=.28, rely=.39)

customerSignInErrorLabel = Label(customerSignInPage)
customerSignInErrorLabel.place(relx=.265, rely=.44)


#newAccount
newFirstNameLabel = Label(newAccountPage, text='Enter Your First Name', font=('Helvetica Bold', 15))
newFirstNameLabel.place(relx=.24, rely=.05)

newFirstNameEntry = Entry(newAccountPage, width=25)
newFirstNameEntry.place(relx=.28, rely=.1)

newMiddleNameLabel = Label(newAccountPage, text="Enter Your Middle Name (Optional)", font=('Helvetica Bold', 15))
newMiddleNameLabel.place(relx=.1, rely=.15)

newMiddleNameEntry = Entry(newAccountPage, width=25)
newMiddleNameEntry.place(relx=.28, rely=.2)

newLastNameLabel = Label(newAccountPage, text="Enter Your Last Name", font=('Helvetica Bold', 15))
newLastNameLabel.place(relx=.24, rely=.25)

newLastNameEntry = Entry(newAccountPage, width=25)
newLastNameEntry.place(relx=.28, rely=.3)

newEmailLabel = Label(newAccountPage, text="Enter Your Email", width=25, font=('Helvetica Bold', 15))
newEmailLabel.place(relx=.1, rely=.35)

newEmailEntry = Entry(newAccountPage, width=25)
newEmailEntry.place(relx=.28, rely=.4)

newAddressLabel = Label(newAccountPage, text="Enter Your Address", width=25, font=('Helvetica Bold', 15))
newAddressLabel.place(relx=.1, rely=.45)

newAddressEntry = Entry(newAccountPage, width=25)
newAddressEntry.place(relx=.28, rely=.5)

newAccountEnterButton = Button(newAccountPage, text="Enter", command=lambda:newUser(newFirstNameEntry.get(), newMiddleNameEntry.get(), newLastNameEntry.get(), newEmailEntry.get(), newAddressEntry.get()))
newAccountEnterButton.place(relx=.28, rely=.55)

newBackToCustomerButton = Button(newAccountPage, text="Return Back", command=lambda: newFrame(newAccountPage, customerSignInPage))
newBackToCustomerButton.place(relx=.28, rely=.6)

newAccountErrorLabel = Label(newAccountPage)
newAccountErrorLabel.place(relx=.18, rely=.65)

#profilePage

greetingLabel = Label(profilePage, text="Hello, ")
greetingLabel.place(relx=.60, rely=.05)

uidReminderLabel = Label(profilePage, text='uid=uid')
uidReminderLabel.place(relx=.1, rely=.05)

emailReminderLabel = Label(profilePage, text='email=email')
emailReminderLabel.place(relx=.1, rely=.10)

subscriptionLabel = Label(profilePage, text='subscription=subscription')
subscriptionLabel.place(relx=.1, rely=.15)

subscriptionButton = Button(profilePage, command=lambda:changeSubscription(), text="Change Subscription Status")
subscriptionButton.place(relx=.2, rely=.15)

viewSalesHistoryButton = Button(profilePage, text="View Sales History",command = lambda: newFrame(profilePage, salesHistoryPage), font=('Helvetica Bold', 15))
viewSalesHistoryButton.place(relx=.1, rely=.2)

viewTrackingOrdersButton = Button(profilePage, text="View Tracking Orders", command= lambda: newFrame(profilePage, trackingOrderPage), font=('Helvetica Bold', 15))
viewTrackingOrdersButton.place(relx=.1, rely=.25)

viewCardsButton = Button(profilePage, text="View Cards", command= lambda: newFrame(profilePage, cardPage), font=('Helvetica Bold', 15))
viewCardsButton.place(relx=.1, rely=.3)

changeInformationButton = Button(profilePage, text="Change Your Information", command=lambda:newFrame(profilePage, changeInfoPage), font=('Helvetica Bold', 15))
changeInformationButton.place(relx=.1, rely=.35)

profileToMainPageButton = Button(profilePage, text="Return to Main Page", command= lambda: newFrame(profilePage, mainPage), font=('Helvetica Bold', 15))
profileToMainPageButton.place(relx=.1, rely=.7)

logOutButton = Button(profilePage, text="Log Out", command= lambda: logOut(), font=('Helvetica Bold', 15))
logOutButton.place(relx=.6, rely=.7)

#salesHistory

salesToProfileButton = Button(salesHistoryPage, text = "Go Back", command=lambda: newFrame(salesHistoryPage, profilePage), font=('Helvetica Bold', 15))
salesToProfileButton.place(relx=.1, rely=.1)

salesHistoryRefreshButton = Button(salesHistoryPage, text="Refresh", command=lambda: viewSalesHistory(), font=('Helvetica Bold', 15))
salesHistoryRefreshButton.place(relx=.2, rely=.1)

salesHistoryLabel = Label(salesHistoryPage)
salesHistoryLabel.place(relx=0, rely=.15)

#trackingOrders

trackingToProfileButton = Button(trackingOrderPage, text = "Go Back", command=lambda: newFrame(trackingOrderPage, profilePage), font=('Helvetica Bold', 15))
trackingToProfileButton.place(relx=.1, rely=.1)

trackingOrderRefreshButton = Button(trackingOrderPage, text="Refresh", command=lambda: viewTrackingOrders())
trackingOrderRefreshButton.place(relx=.2, rely=.1)

trackingHistoryLabel = Label(trackingOrderPage)
trackingHistoryLabel.place(relx=.01, rely=.15)

#card page
cardToProfileButton = Button(cardPage, text = "Go Back", command=lambda: newFrame(cardPage, profilePage), font=('Helvetica Bold', 15))
cardToProfileButton.place(relx=.1, rely=.1)

cardRefreshButton = Button(cardPage, text="Refresh", command=lambda: viewCards())
cardRefreshButton.place(relx=.2, rely=.1)

addOrDropNewCardButton = Button(cardPage, text='Add/Drop Card', command=lambda: newFrame(cardPage, addCardPage))
addOrDropNewCardButton.place(relx=.45, rely=.1)

cardLabel = Label(cardPage)
cardLabel.place(relx=.01, rely=.15)

#add card page
addCardBackButton = Button(addCardPage, text ="Back to Cards", command=lambda: newFrame(addCardPage, cardPage))
addCardBackButton.place(relx=.25, rely=.6)

addCardNumberLabel = Label(addCardPage, text = "Enter Your Card Number",font=('Helvetica Bold', 15))
addCardNumberLabel.place(relx=.25, rely=.1)

addCardNumberEntry = Entry(addCardPage)
addCardNumberEntry.place(relx=.25, rely=.17)

addCardBalanceLabel = Label(addCardPage, text = "Enter Your Card Balance",font=('Helvetica Bold', 15))
addCardBalanceLabel.place(relx=.25, rely=.23)

addCardBalanceEntry = Entry(addCardPage)
addCardBalanceEntry.place(relx=.25, rely=.3)

addCardTypeString = tkinter.StringVar()
addCardTypeString.set("Select Your Card Type")
addCardType = OptionMenu(addCardPage, addCardTypeString, "Credit", "Debit")
addCardType.place(relx=.25, rely=.35)

addCardButton = Button(addCardPage, text ="Add Card", command=lambda: addCard(addCardNumberEntry.get(), addCardBalanceEntry.get(), addCardTypeString.get()))
addCardButton.place(relx=.25, rely=.45)

addCardErrorLabel = Label(addCardPage, text="")
addCardErrorLabel.place(relx=.25, rely=.75)

dropCardButton = Button(addCardPage, text ="Drop Card/s", command=lambda: newFrame(addCardPage, dropCardPage))
dropCardButton.place(relx=.25, rely=.53)

#drop Card Page
dropCardBackButton = Button(dropCardPage, text ="Back to Cards", command=lambda: newFrame(dropCardPage, cardPage))
dropCardBackButton.place(relx=.25, rely=.6)

dropCardNumberLabel = Label(dropCardPage, text = "Enter the Card Number You want to Remove",font=('Helvetica Bold', 15))
dropCardNumberLabel.place(relx=.25, rely=.13)

dropCardNumberEntry = Entry(dropCardPage)
dropCardNumberEntry.place(relx=.25, rely=.2)

dropCardButton = Button(dropCardPage, text="Drop Card", command=lambda:dropCard(dropCardNumberEntry.get()))
dropCardButton.place(relx=.25, rely=.3)

dropCardErrorLabel = Label(dropCardPage, text="")
dropCardErrorLabel.place(relx=.25, rely=.75)

#change information page
changeInfoFirstNameLabel = Label(changeInfoPage, text='Re-Enter Your First Name', font=('Helvetica Bold', 15))
changeInfoFirstNameLabel.place(relx=.24, rely=.05)

changeInfoFirstNameEntry = Entry(changeInfoPage, width=25)
changeInfoFirstNameEntry.place(relx=.28, rely=.1)

changeInfoMiddleNameLabel = Label(changeInfoPage, text="Re-Enter Your Middle Name (Optional)", font=('Helvetica Bold', 15))
changeInfoMiddleNameLabel.place(relx=.1, rely=.15)

changeInfoMiddleNameEntry = Entry(changeInfoPage, width=25)
changeInfoMiddleNameEntry.place(relx=.28, rely=.2)

changeInfoLastNameLabel = Label(changeInfoPage, text="Re-Enter Your Last Name", font=('Helvetica Bold', 15))
changeInfoLastNameLabel.place(relx=.24, rely=.25)

changeInfoLastNameEntry = Entry(changeInfoPage, width=25)
changeInfoLastNameEntry.place(relx=.28, rely=.3)

changeInfoEmailLabel = Label(changeInfoPage, text="Re-Enter Your Email", width=25, font=('Helvetica Bold', 15))
changeInfoEmailLabel.place(relx=.1, rely=.35)

changeInfoEmailEntry = Entry(changeInfoPage, width=25)
changeInfoEmailEntry.place(relx=.28, rely=.4)

changeInfoAddressLabel = Label(changeInfoPage, text="Re-Enter Your Address", width=25, font=('Helvetica Bold', 15))
changeInfoAddressLabel.place(relx=.1, rely=.45)

changeInfoAddressEntry = Entry(changeInfoPage, width=25)
changeInfoAddressEntry.place(relx=.28, rely=.5)

changeInfoAccountEnterButton = Button(changeInfoPage, text="Enter", command=lambda:changeInfo(changeInfoFirstNameEntry.get(), changeInfoMiddleNameEntry.get(), changeInfoLastNameEntry.get(), changeInfoEmailEntry.get(), changeInfoAddressEntry.get()))
changeInfoAccountEnterButton.place(relx=.28, rely=.55)

changeInfoBackToCustomerButton = Button(changeInfoPage, text="Return Back", command=lambda: newFrame(changeInfoPage, profilePage))
changeInfoBackToCustomerButton.place(relx=.28, rely=.6)

changeInfoAccountErrorLabel = Label(changeInfoPage)
changeInfoAccountErrorLabel.place(relx=.18, rely=.65)


#shopping cart page
shoppingCartBackButton = Button(shoppingCartPage, text="Go Back", command=lambda: newFrame(shoppingCartPage, mainPage))
shoppingCartBackButton.place(relx=.05, rely=.05)

shoppingCartListBox = Listbox(shoppingCartPage, width=80)
shoppingCartListBox.place(relx=.05, rely=.1)

shoppingCartDeleteButton = Button(shoppingCartPage, text="Remove From Shopping Cart", command=lambda: deleteItems())
shoppingCartDeleteButton.place(relx=.35, rely=.05)

shoppingCartCheckOutButton = Button(shoppingCartPage, text='Check Out', command=lambda: checkOut())
shoppingCartCheckOutButton.place(relx=.75, rely=.05)

shoppingCartErrorLabel = Label(shoppingCartPage)
shoppingCartErrorLabel.place(relx=.05, rely=.8)


# ShoppingScrollbar
ShoppingScrollbar = Scrollbar(shoppingCartPage, orient=VERTICAL)
ShoppingScrollbar.config(command=shoppingCartListBox.yview)
ShoppingScrollbar.place(relx=.83,rely=.1,height=165)
shoppingCartListBox.config(yscrollcommand=ShoppingScrollbar.set)

#check out page
checkOutBackButton = Button(checkOutPage, text='Return to Shopping Cart', command=lambda:newFrame(checkOutPage, shoppingCartPage))
checkOutBackButton.place(relx=.05, rely=.05)

checkOutErrorLabel = Label(checkOutPage, text='')
checkOutErrorLabel.place(relx=.5, rely=.85)

checkOutOnlineButton = Button(checkOutPage, text="Checkout Online", command=lambda: onlineCheckOut())
checkOutOnlineButton.place(relx=.15, rely=.2)

creditMenuStringVar = tkinter.StringVar()
creditMenuStringVar.set("Please select a card")
checkOutCreditMenu = OptionMenu(checkOutPage, creditMenuStringVar, "Please select a card")
checkOutCreditMenu.place(relx=.1)

checkOutOfflineButton = Button(checkOutPage, text="Store Pickup", command= lambda: offlineCheckOut())
checkOutOfflineButton.place(relx=.55, rely=.2)

db=sqlite3.connect(dbfilepath)
cursor=db.cursor()
cursor.execute("select distinct w_id from Warehouse")
tempWareHouseList=cursor.fetchall()
warehouseList=list()
warehouseList.append("Choose a shipper")
for x in tempWareHouseList:
    warehouseList.append(x[0])

tempWareHouseStringVar=tkinter.StringVar()
tempWareHouseStringVar.set("Choose a shipper")
checkOutOnlineShipperList = OptionMenu(checkOutPage, tempWareHouseStringVar, *warehouseList)
checkOutOnlineShipperList.place(relx=.15, rely=.25)

cursor.execute("select distinct s_id from Store")
tempStoreList=cursor.fetchall()
storeList=list()
storeList.append("Choose a store")
for x in tempStoreList:
    storeList.append(x[0])

tempStoreStringVar=tkinter.StringVar()
tempStoreStringVar.set("Choose a store")
checkOutOfflineStoreList = OptionMenu(checkOutPage, tempStoreStringVar, *storeList)
checkOutOfflineStoreList.place(relx=.55, rely=.25)
db.close()

checkOutSubscriberStringVar = tkinter.StringVar()
checkOutSubscriberStringVar.set("Purchase as subscriber")

checkOutSubscriberModeOptionMenu = OptionMenu(checkOutPage, checkOutSubscriberStringVar, "Purchase as subscriber", "Purchase as nonsubscriber")
checkOutSubscriberModeOptionMenu.place(relx=.7)

checkOutTotalPriceLabel = Label(checkOutPage, text="")
checkOutTotalPriceLabel.place(rely=.9)



root.resizable(0, 0)
root.mainloop()




#actual checkout system(online, offline, enough balance, ask for shipper)
#appearance cleanup
#cry anyways


#update er diagram after everything
