#!/usr/bin/python3
import os
from console import app, db

if __name__ == "__main__":
    db.init_db(os.path.dirname(os.path.realpath(__file__)) + "/console/schema.sql")
    app.run(host="0.0.0.0", debug=False)
