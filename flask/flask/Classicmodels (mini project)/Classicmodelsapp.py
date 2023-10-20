from flask import Flask
from flask import abort
from flask import request
from flask_cors import CORS
import pymysql
import json
import math



app = Flask(__name__)
CORS(app)

MAX_PAGE_SIZE = 10


@app.route("/")
def greetings():
    return """<html> 
    <h1 style="color:olive;"> Hello, Welcome to the Classic Models API! 🎉 </h1>
    <p> To use it, please read the information below: </p>
    <h2 style="color:teal;"> Employees  </h2>

    <p> To find the information related to all employees, try the <b>/employees</b> endpoint. At the <b>bottom</b> of each page, you'll find the links to access the next and last pages </p>
    <p> To find the information related to ONE employee, try the <b>/employees/{ID}</b> endpoint. </p>
    <p> To search for an employee's name directly in the URL, try the <b>/employees?name={NAME}</b> endpoint. </p>
    <h2 style="color:teal;"> Customers </h2>
    <p> To find the information related to all customers, try the <b>/customers</b> endpoint. At the <b>bottom</b> of each page, you'll find the links to access the next and last pages </p> 
    <p> To find the information related to ONE customer, try the <b>/customers/{ID}</b> endpoint. </p>
    <p> To search for a customer's name directly in the URL, try the <b>/customers?name={NAME}</b> endpoint. </p>
    <h2 style="color:teal;"> Products </h2>
    <p> To find the information related to all products, try the <b>/products</b> endpoint. At the <b>bottom</b> of each page, you'll find the links to access the next and last pages </p> 
    <p> To <b>update</b> the information related to ONE specific product, you'll have to make a PUT request to the endpoint <b>/product/{ID}?quantity_in_stock={value}&product_line={value}&product_price={value}</b>.
</br>
Happy searching!🙂
    
    </html>"""

@app.route("/customers")
def customers():
    name = request.args.get('name')
    page = int(request.args.get('page', 0))
    page_size = int(request.args.get('page_size', MAX_PAGE_SIZE))
    page_size = min(page_size, MAX_PAGE_SIZE)
    db_conn = pymysql.connect(user='root',host="localhost", password="N956124A", database="classicmodels",
                              cursorclass=pymysql.cursors.DictCursor)
    with db_conn.cursor() as cursor:
        if name:
            cursor.execute("""SELECT 
                c.customerNumber AS Customer_ID, 
                c.customerName AS Customer_name, 
                CONCAT_WS(' ', c.contactFirstName, c.contactLastName) AS Contact_name, 
                c.phone AS Phone_number, 
                CONCAT_WS(' ', c.addressLine1, c.city, c.state, c.postalCode) AS Full_address, 
                c.country AS Country, 
                CASE
                    WHEN e.employeeNumber IS NULL THEN 'Not available'
                    ELSE CONCAT_WS(' ', e.firstName, e.lastName)
                END AS Sales_representative
                FROM customers c
                LEFT JOIN employees e ON c.salesRepEmployeeNumber = e.employeeNumber
                WHERE c.customerName LIKE %s
                LIMIT %s OFFSET %s""", (f'%{name}%', page_size, page * page_size))
        else:
            cursor.execute("""SELECT 
                c.customerNumber AS Customer_ID, 
                c.customerName AS Customer_name, 
                CONCAT_WS(' ', c.contactFirstName, c.contactLastName) AS Contact_name, 
                c.phone AS Phone_number, 
                CONCAT_WS(' ', c.addressLine1, c.city, c.state, c.postalCode) AS Full_address, 
                c.country AS Country, 
                CASE
                    WHEN e.employeeNumber IS NULL THEN 'Not available'
                    ELSE CONCAT_WS(' ', e.firstName, e.lastName)
                END AS Sales_representative
                FROM customers c
                LEFT JOIN employees e ON c.salesRepEmployeeNumber = e.employeeNumber
                LIMIT %s OFFSET %s""", (page_size, page * page_size))

        customers = cursor.fetchall()

    with db_conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS total FROM customers")
        total = cursor.fetchone()
        last_page = math.ceil(total['total'] / page_size)

    db_conn.close()
    return {
        'customers': customers,
        'next_page': f'/customers?page={page + 1}&page_size={page_size}&name={name}',
        'last_page': f'/customers?page={last_page}&page_size={page_size}&name={name}',
    }


@app.route("/customers/<int:Customer_ID>")
def customer(Customer_ID):
    page = int(request.args.get('page', 0))
    db_conn = pymysql.connect(user='root',host="localhost", password="N956124A", database="classicmodels",
                              cursorclass=pymysql.cursors.DictCursor)
    with db_conn.cursor() as cursor:
        cursor.execute("""SELECT 
    c.customerNumber AS Customer_ID, 
    c.customerName AS Customer_name, 
    CONCAT_WS(' ', c.contactFirstName, c.contactLastName) AS Contact_name, 
    c.phone AS Phone_number, 
    CONCAT_WS(' ', c.addressLine1, c.city, c.state, c.postalCode) AS Full_address, 
    c.country AS Country, 
    CASE
        WHEN e.employeeNumber IS NULL THEN 'Not available'
        ELSE CONCAT_WS(' ', e.firstName, e.lastName)
    END AS Sales_representative
FROM customers c
LEFT JOIN employees e ON c.salesRepEmployeeNumber = e.employeeNumber
WHERE c.customerNumber = %s;""", (Customer_ID,))
        customer = cursor.fetchone()
    if not customer:
        abort(404)
    db_conn.close() 
    return customer


@app.route("/employees")
def employees():
    page = int(request.args.get('page', 0))
    page_size = int(request.args.get('page_size', MAX_PAGE_SIZE))
    page_size = min(page_size, MAX_PAGE_SIZE)
    name = request.args.get('name', None)

    db_conn = pymysql.connect(user='root', host="localhost", password="N956124A", database="classicmodels",
                              cursorclass=pymysql.cursors.DictCursor)

    if name:
        with db_conn.cursor() as cursor:
            cursor.execute("""SELECT e.employeeNumber as Employee_ID, 
            CONCAT_WS(' ', e.firstName, e.lastName) AS Full_name, e.email AS Email, e.extension AS Extension,
            e.jobTitle AS Job_title, CONCAT_WS(' ', e1.firstName, e1.lastName) AS Manager,o.city AS Office_location
            FROM employees e
            LEFT JOIN offices o ON e.officeCode = o.officeCode
            LEFT JOIN employees e1 ON e.reportsTo=e1.employeeNumber
            WHERE CONCAT_WS(' ', e.firstName, e.lastName) LIKE %s LIMIT %s OFFSET %s""",
                           (f'%{name}%', page_size, page * page_size))
            employees = cursor.fetchall()
        
        db_conn.close()
        return {'employees': employees}

    else:
        with db_conn.cursor() as cursor:
            cursor.execute("""SELECT e.employeeNumber as Employee_ID, 
            CONCAT_WS(' ', e.firstName, e.lastName) AS Full_name, e.email AS Email, e.extension AS Extension,
            e.jobTitle AS Job_title, CONCAT_WS(' ', e1.firstName, e1.lastName) AS Manager,o.city AS Office_location
            FROM employees e
            LEFT JOIN offices o ON e.officeCode = o.officeCode
            LEFT JOIN employees e1 ON e.reportsTo=e1.employeeNumber LIMIT %s OFFSET %s""", (page_size, page * page_size))
            employees = cursor.fetchall()

        with db_conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS total FROM employees")
            total = cursor.fetchone()
            last_page = math.ceil(total['total'] / page_size)

        db_conn.close()
        return {
            'employees': employees,
            'next_page': f'/employees?page={page + 1}&page_size={page_size}',
            'last_page': f'/employees?page={last_page}&page_size={page_size}',
        }


@app.route("/employees/<int:Employee_ID>")
def employee(Employee_ID):
    page = int(request.args.get('page', 0))
    db_conn = pymysql.connect(user='root',host="localhost", password="N956124A", database="classicmodels",
                              cursorclass=pymysql.cursors.DictCursor)
    with db_conn.cursor() as cursor:
        cursor.execute("""SELECT e.employeeNumber as Employee_ID, CONCAT_WS(' ', e.firstName, e.lastName) AS Full_name, 
        e.email AS Email, e.extension AS Extension, e.jobTitle AS Job_title, CONCAT_WS(' ', e1.firstName, e1.lastName) AS Manager,
        o.city AS Office_location
        FROM employees e
        LEFT JOIN offices o ON e.officeCode = o.officeCode
        LEFT JOIN employees e1 ON e.reportsTo=e1.employeeNumber
        WHERE e.employeeNumber = %s;""", (Employee_ID,))
        employee = cursor.fetchone()
    if not employee:
        abort(404)
    db_conn.close() 
    return employee

@app.route("/products")
def products():
    page = int(request.args.get('page', 0))
    page_size = int(request.args.get('page_size', MAX_PAGE_SIZE))
    page_size = min(page_size, MAX_PAGE_SIZE)

    db_conn = pymysql.connect(user='root',host="localhost", password="N956124A", database="classicmodels",
                              cursorclass=pymysql.cursors.DictCursor)
    with db_conn.cursor() as cursor:
        cursor.execute("""
            SELECT productCode AS Product_ID, productName AS Product_name, productLine AS Product_line, 
            productscale AS Product_scale, productVendor AS Product_vendor, productDescription AS Product_description, 
            quantityInStock AS Quantity_available, buyPrice AS Price, MSRP
            FROM products
            LIMIT %s
            OFFSET %s
        """, (page_size, page * page_size))
        products = cursor.fetchall()

    with db_conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS total FROM products")
        total = cursor.fetchone()
        last_page = math.ceil(total['total'] / page_size)

    db_conn.close()
    return {
        'products': products,
        'next_page': f'/products?page={page+1}&page_size={page_size}',
        'last_page': f'/products?page={last_page}&page_size={page_size}',}

@app.route("/product/<Product_ID>")
def showproduct(Product_ID):
    page = int(request.args.get('page', 0))
    page_size = int(request.args.get('page_size', MAX_PAGE_SIZE))
    page_size = min(page_size, MAX_PAGE_SIZE)

    db_conn = pymysql.connect(user='root',host="localhost", password="N956124A", database="classicmodels",
                              cursorclass=pymysql.cursors.DictCursor)
    with db_conn.cursor() as cursor:
        cursor.execute("""
            SELECT productCode AS Product_ID, productName AS Product_name, productLine AS Product_line, 
            productscale AS Product_scale, productVendor AS Product_vendor, productDescription AS Product_description, 
            quantityInStock AS Quantity_available, buyPrice AS Price, MSRP
            FROM products
            LIMIT %s
            OFFSET %s
        """, (page_size, page * page_size))
        products = cursor.fetchall()

    with db_conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS total FROM products")
        total = cursor.fetchone()
        last_page = math.ceil(total['total'] / page_size)

    db_conn.close()
    return {
        'products': products,
        'next_page': f'/products?page={page+1}&page_size={page_size}',
        'last_page': f'/products?page={last_page}&page_size={page_size}',}

@app.route("/product/<Product_ID>",methods=["PUT"])
def product(Product_ID):
    data = request.get_json()
    quantity_in_stock = data.get('quantity_in_stock')
    product_line = data.get('product_line')
    product_price = data.get('product_price')
    db_conn = pymysql.connect(user='root',host="localhost", password="N956124A", database="classicmodels",
                              cursorclass=pymysql.cursors.DictCursor)
    with db_conn.cursor() as cursor:
        cursor.execute("""
                UPDATE products
                SET quantityinstock = %s,
                    productline = %s,
                    buyprice = %s
                WHERE productcode = %s
            """, (quantity_in_stock, product_line, product_price, Product_ID))
        db_conn.commit()

    db_conn.close()
    return ({'message': 'Product has been updated successfully'}),200

