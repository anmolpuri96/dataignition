#!/usr/bin/python3
from flask_app import app
# app.run(debug=True, host="0.0.0.0", port=80)
app.run(debug=True, ssl_context=('ssl.cert', 'ssl.key'), port=443)
