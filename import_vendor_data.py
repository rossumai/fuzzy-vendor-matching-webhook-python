#!/usr/bin/env python3
#
# Usage: import_vendor_data.py supportive_data/vendor_data_de.csv

import csv
import sys

from database.database import DEDatabase

db = DEDatabase()


def vendor_import(row):
    """Insert named rows in the order appropriate for the database schema.

    :param row: Row with data in the imported csv file.
    """
    db.execute('INSERT INTO vendor_data VALUES (' + ', '.join(['%s' for _ in range(15)]) + ')',
               list(row[k] for k in ['VendorID', 'VendorName', 'Address1', 'Address2', 'Address3',
                                     'City', 'State', 'ZipCode', 'Country', 'Telephone', 'VendorAccountGroup',
                                     'IndustrySector', 'TaxID1', 'ActiveVendor', 'FileID']))


def db_import(filename):
    """Create vendor table and import active vendors to it.

    :param filename: CSV file with vendor data.
    """
    db.execute("""CREATE TABLE IF NOT EXISTS vendor_data (
                id VARCHAR(16) PRIMARY KEY,
                name TEXT NOT NULL,
                address1 TEXT,
                address2 TEXT,
                address3 TEXT,
                city TEXT,
                state TEXT,
                zipcode TEXT,
                country TEXT,
                telephone TEXT,
                vendor_account_group TEXT,
                industry_sector TEXT,
                taxid1 TEXT,
                active_vendor INT NOT NULL,
                file_id TEXT);""")

    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            if row['ActiveVendor'] == '1':
                vendor_import(row)
    db.commit()


if __name__ == "__main__":
    db_import(sys.argv[1])
