# Webshop Template with Flask, SQL Alchemy, Stripe Integration and Render Deployment

This is a basic webshop template built with Flask and SQL Alchemy, with Stripe integration for payments, and deployed on Render for testing and development purposes. The template includes a basic storefront layout, a shopping cart functionality, and a checkout process with Stripe integration.

## Getting Started
To get started with this webshop template, you will need to have Python and pip installed on your machine. You can clone the repository from GitHub and install the required dependencies by running the following commands:

```
git clone https://github.com/your_username/your_repository.git
cd your_repository
pip install -r requirements.txt
```

Once you have installed the dependencies, you will need to set up your environment variables. Rename the .env.example file to .env and replace the placeholders with your own Stripe API keys.

```
STRIPE_PUBLIC_KEY=your_stripe_public_key
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_ENDPOINT_SECRET=your_endpoint_secret
```

Running the Application
To run the application, you can use the following command:

```
gunicorn -w 4 'application:create_app()'
```
This will start a local server on http://localhost:8000.

## Deployment
This webshop template is set up for deployment on Render. You will need to create an account on Render and set up a new web service. Once you have set up your web service, you can link it to your GitHub repository and Render will automatically deploy any changes that you push to the master branch.

### Testing
To test the application, you can use the Stripe test API keys. You can create a test checkout session by navigating to http://localhost:5000/checkout. This will redirect you to the Stripe checkout page, where you can complete the test payment using the following card information:

```
Card number: 4242 4242 4242 4242
Expiration date: Any future date
CVC: Any 3 digits
```

## Credits
This webshop template was built with the help of the following libraries:

* Flask: A micro web framework for Python
* SQL Alchemy: A Python SQL toolkit and ORM
* Stripe: A payment processing platform
* Render: A cloud platform for deploying and scaling web applications

## License
This webshop template is licensed under the MIT License. See LICENSE for more information.