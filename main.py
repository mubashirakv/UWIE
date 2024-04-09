from flask import*
from public import*
from admin import*
from resteam import*
from staff import*

app=Flask(__name__)

app.register_blueprint(public)
app.register_blueprint(admin)
app.register_blueprint(resteam)
app.register_blueprint(staff)
app.secret_key='3443'

app.run(debug=True,port=5005)