TradeBay - Barter Platform
Welcome to TradeBay, a web-based platform where users can barter items instead of purchasing them! The platform enables users to offer items they own and request items from others, facilitating trades between users without the exchange of money.

Website Overview
TradeBay is designed to allow users to create, manage, and engage in item trades. Users can list items they want to offer and specify items they are looking for. The app connects users to trade goods, fostering a community of exchange without monetary transactions.
Here is a link to the deployed website on render: https://trade-bay-capstone-proj.onrender.com.

Features Implemented
1. User Authentication
Feature: Users can sign up, log in, and maintain a personalized account.
Reason: User authentication is essential for ensuring that trades are made between verified users and that each user has a unique profile and set of items to trade.
2. Item Listing (Offering and Requesting)
Feature: Users can list items they wish to offer and specify the items they are seeking.
Reason: A core component of the platform is the ability for users to engage in trade, and this requires categorizing items as offered or requested.
3. Trade Proposals and Acceptance
Feature: Users can propose trades by offering items in exchange for requested items, and the trade status can be updated to ‘Pending’ or ‘Accepted’.
Reason: The ability to propose and accept trades is fundamental to a barter system. This feature ensures that users can negotiate trades and formalize agreements.
4. Item Management (Remove and Update)
Feature: Users can remove items from their offered or requested lists and update them as needed.
Reason: Keeping the list of items up to date ensures that users only display items they are willing to trade, enhancing the credibility and functionality of the site.
5. CSRF Protection
Feature: Security features such as Cross-Site Request Forgery (CSRF) protection are in place.
Reason: This prevents unauthorized users from performing malicious actions on behalf of logged-in users.
User Flow
Sign Up / Log In: Users begin by creating an account or logging in if they already have one.
Profile Management: Once logged in, users can update their profile with an avatar, email, and username.
Item Listing: Users can then list items they want to offer or request.
View and Propose Trades: Users can browse other users' offerings and propose trades.
Accept Trades: When a trade is proposed, the receiving user can choose to accept or decline the trade.
Complete Trade: Once a trade is accepted, the status is updated, and users receive confirmation of the agreement.
API Overview
The eBay API is used to fetch item information, such as title, condition, and images, from eBay listings.

Endpoint: The findItemsAdvanced endpoint is used to fetch items related to search keywords.
Notes:
Fetch requests are limited to 10 items per search to avoid overwhelming the user with results.
Items fetched from eBay are cross-checked with the TradeBay database to ensure they are unique.

Technology Stack
Backend:

Flask: A Python-based web framework that powers the backend of the app.
SQLAlchemy: ORM for database management.
PostgreSQL: The primary database used for storing user, item, and trade data.
Frontend:

HTML/CSS: Used for rendering pages.
JavaScript: For handling frontend logic, such as making API calls and managing the DOM dynamically.
Security:

Flask-WTF: For handling forms with CSRF protection.
Bcrypt: For secure password hashing.
Deployment:

Render: The platform used to deploy the application.
Running the Application
Install dependencies:
Use the requirements.txt file to install necessary Python libraries:

pip install -r requirements.txt
Set up environment variables:
Use the .env file to store secrets, such as the SECRET_KEY and database credentials.

Database Migrations:
Run the following commands to apply migrations:
flask db upgrade

Start the Application:
Run the app locally using:
flask run

Explore TradeBay today and start trading items without the need for cash!