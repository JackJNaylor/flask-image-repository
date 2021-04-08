# Flask Image Marketplace
## Welcome to the Flask Image Marketplace
### By Jack Naylor

### How to Run
Navigate to the directory ShopifyImageRepo2021. Run these commands in this order.
python3 -m venv auth
source auth/bin/activate
pip install flask flask-sqlalchemy flask-login
export FLASK_APP=Project
export FLASK_DEBUG=1
flask run

The application should be available to view in a web browser at the given address, usually http://127.0.0.1:5000/ .


### How to Use

Upon visiting the application you will be required to sign up and make an account. Next, use you're credentials to log in to the application. Some sample images have been included in the /Project/static/img folder, but the user may upload any images they would like with the Upload Image button located in the header. The user will be prompted to enter the price they wish to sell the image, the inventory (number of images available for sale) and a description of the image. There is also the ability to make the image private so only the user who uploads it may view it. All of these can be updated and changed after the image has been uploaded as well. If the image was made private, the user will be able to see it on their profile, but it will not appear on the home feed of other users. If the user has an uploaded image that is not private, they can log out and make a new account to view the ordering feature. On the home page in the new account, they will see all images that have not been made private by their viewers. Images can be clicked on to see their description and can be ordered. Your orders will appear under the 'Your Orders' page in the header. By switching back to the original account, you will see the revenue tracker on the user's profile will have updated with the sum of all price of all orders of their images. You can also view orders people have made for your images and update their status (In Progress, Delivered, ect) on the 'Outgoing Orders' page linked in the header. 
