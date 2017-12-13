# Categories and Items project
This Website allows you to store items in a database. The items are categorized by categories, which are also created by the user and saved in the database. The Website provides a Google Login system and has authorization control in place. This means that only the user who created an item is eligable to edit or delete the item. Without being logged in, a user cannot create a new item.

## Getting Started
### Installation Requirements
*Note that the explanations given below are for Windows 7*
* **Python**: The Python version used for this project is 2.7.12, which can be found [here](https://www.python.org/downloads/)
* **PostgreSQL**: The PostgreSQL version used for this project is 9.5.9, which can be found [here](https://www.postgresql.org/download/)
* **SQLAlchemy**: Open a terminal (cmd) and type `pip install SQLAlchemy`
* **Flask**: Open a terminal (cmd) and type `pip install Flask`
* **OAuth2**: Open a terminal (cmd) and type `pip install oauth2client`

### Google Developer Account
1. Navigate to the Google Developer Website [here](https://developers.google.com)
2. Select the **Google API Console**
3. Create a new project
4. Choose **Credentials**
5. Add **http://localhost:5000** to the authorized JavaScript sources
6. Adjust the Consent screen accordingly
7. After receiving your Client-ID and Client key, download JSON
8. Rename the downloaded file to **client_secrets.json**
9. Save the file in the same folder as the **itemproject.py** file


### Creating a database
1. Open a terminal (cmd) and type `psql -U postgres` to use the default user in postgresql
2. Type `CREATE DATABASE items_db;`
3. You can exit now by typing `CTRL+C`


### Using example Categories and Items (Optional)
You can start this project with an empty database and can manually create Categories and Items. If you want to, however, you can load the **starting_data.py** file to load some categories and items initially. Note that you cannot edit or delet this items and categories via the web interface as they were created with fictive user credentials.

1. Open a terminal and `cd` into the folder, in which you saved the file
2. Type `python starting_data.py`


### Run the Code
1. Open a terminal and `cd` into the folder, in which you saved the file
2. Type `python itemproject.py`
3. Open a browser and type `localhost:5000/index` (*Note: If you want to use a different port, you can change this in line 382 of the itemproject.py file*)
