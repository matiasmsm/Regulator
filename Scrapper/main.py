import psycopg2
from psycopg2 import sql

#from Africa import scrape_africa
from Asia import get_asia
from LATAM import get_latam
"""from EU import get_eu
from ME import scrape_me
from NA import scrape_na
from Oceania import scrape_oceania"""

import os
from dotenv import load_dotenv



# Load environment variables from .env file
load_dotenv()

# Get the values from environment variables
host = os.getenv('DATABASE_HOST')
dbname = os.getenv('DATABASE_NAME')
user = os.getenv('DATABASE_USER')
password = os.getenv('DATABASE_PASSWORD')
port = os.getenv('DATABASE_PORT', 5432)  # Default to 5432 if not set


def save_db(regulations_list):
    try:
        # Establish the connection here (make sure you have already loaded .env variables)
        connection = psycopg2.connect(
            host=host,
            dbname=dbname,
            user=user,
            password=password
        )

        # Open a cursor to perform database operations
        with connection.cursor() as cursor:
            for data in regulations_list:
                # Insert data into the 'regulations' table
                cursor.execute(
                    """
                    INSERT INTO "Regulations" (title, summary, country, entity, link, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """, 
                    (data['Title'], data['Summary'], data['Country'], data['Entity'], data['Link'], data['Timestamp'])
                )

            # Commit the transaction
            connection.commit()

    except Exception as e:
        print(f"Error saving to the database: {e}")
    
    finally:
        # Close the connection if it was established
        if connection:
            connection.close()

    print("Data saved successfully!")


def scrape_regulatory_agencies():
    latam_list = get_latam.scrape()

    asia_list = get_asia.scrape()
    #eu_list = get_eu()
    """ 
        africa_dict = scrape_africa()
        me_dict = scrape_me()
        na_dict = scrape_na()
        oceania_dict = scrape_oceania()
    """
    merged_list = asia_list + latam_list
    save_db(merged_list)
    return


if __name__ == '__main__':
    scrape_regulatory_agencies()