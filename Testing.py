# /// script
# requires-python = ">= 3.14.6" 

#Class for items to be added
class item:

#Variables




    #Assigns the varaibles to an object
    def __init__(self, *inp):

        #Checks how many parameters there are
        if len(inp) == 3:
            self.prodName: str = inp[0]
            self.prodID: int = inp[1]
            self.prodStock: int = inp[2]
        elif len(inp) == 4:
            self.prodName: str = inp[0]
            self.prodID: int = inp[1]
            self.prodStock: int = inp[2]
            self.prodOpID: int = inp[3]
        else:
            print("Invalid Entry")

def addNewItem():
    print("Please input the corresponding entry for registering a new product")
    print("New Product Entry Name")
    newProdName = input(">>")
    print("New Product Entry ID")
    newProdID = input(">>")
    print("New Product Current Amount In Stock")
    newProdStock = input(">>")
    print("Optional Extra ID thing, Type N or n to skip")
    newOptionalID = input(">>")

    if newOptionalID == "N" or newOptionalID == "n":
        testProd = item(newProdName, newProdID, newProdStock)
        allItems.append(testProd)
        
    else:
        testProd = item(newProdName, newProdID, newProdStock, newOptionalID)
        allItems.append(testProd)
        
allItems = []

addNewItem()

print(allItems[0].prodName)
