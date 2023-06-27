# The CEng
#### Video Demo:  https://youtu.be/snF_QyvRu6Y
#### Description: A website which offers help to civil engineers who want to become professionally qualified.

## :computer: Tech Used

- Programming Languages: Python
- Frameworks: Flask
- Web Development: HTML, CSS, Jinja
- Version Control: Git
- API: Stripe

## Structure

#### Home Page / index.html

This website contains the main page (index.html) which includes the Javascript code to provide some dynamism. The design is generally simple, since I like minimalistic design. At the same time, more time was spent on backend functionality that the front-end design elements, since it is much more interesting challenge for me personally.


#### "What is this?" / About page

This page describes what is offered. This is just a simple html page with some css elements. Some of the CSS functionality is employed here to highlight interesting offers. HTML use of unordered list is also observed.

#### Services Page

Here the visitors could see which services are offered and could add the services into the basket. Session cookies and sql are used here in Python Flask to achieve this.

#### Basket

Here visitors could see which products (services) have been added into the basket. The could also remove these from the basket. Python Flask is employed here (cookies and sql).


#### Contact

Visitors could write a message to the admin. Python Flask mail module is used to achieve that.


#### Register

Visitors could register as users.


#### Log In

Registered users could log in. Logging in helps to purchase any products/services.


#### Log Out

Logged In users could log out.


#### Account

Users could change the password and delete the account altogether.

#### Checkout

Checkout button in the basket redirects registered users to purchase the chosen services. Stripe API is employed here. During the checkout, the users could edit the quantity and purchase the products.
