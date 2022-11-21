#import library
import datetime
import os

##import library pendukung
import jwt
from flask import Flask, jsonify, make_response, render_template, request
from flask_cors import CORS
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy

#inisialisai objek flask
app = Flask(__name__)
api = Api(app)
db = SQLAlchemy(app)
CORS(app)

#konfigurasi database ===> create file db.sqlite
filename = os.path.dirname(os.path.abspath(__file__))
database = 'sqlite:///' + os.path.join(filename,'db.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = database
app.config['SECRET_KEY'] = "inirahasia"


#membuat model database User
class UserModel(db.Model):
 id = db.Column(db.Integer, primary_key=True)  
 name = db.Column(db.String(50))
 username = db.Column(db.String(50))
 email = db.Column(db.String(100))
 password = db.Column(db.String(100))

#create model ke dalam file db.sqlite
db.create_all()

class Register(Resource):
   #post data user ke database
   def post(self):
      dataname = request.form.get('name')
      datausername = request.form.get('username')
      dataemail = request.form.get('email')
      datapassword = request.form.get('password')
      #cek username,email  & password ada 
      if dataname and datausername and dataemail and datapassword:
         #post ke db
         user = UserModel(name=dataname, username=datausername,email=dataemail,password=datapassword)
         db.session.add(user)
         db.session.commit()
         return make_response(jsonify({'message':'Register Berhasil',
                                       'data':
                                          {
                                             'name':dataname,
                                             'username':datausername,
                                             'email':dataemail,
                                             }
                                          }),{'code': 200})
      return make_response(jsonify({'msg':'Pastikan Semua field Terisi'}), 404)
   
class Login(Resource):
    #post data user ke database
   def post(self):
      datausername = request.form.get('username')
      datapassword = request.form.get('password')
      #QUERY kecocokan data
      queryUsername =[data.username for data in UserModel.query.all()]
      queryPassword =[data.password for data in UserModel.query.all()]
      if datausername in queryUsername and datapassword in queryPassword : 
         querydata = UserModel.query.filter_by(username=datausername).first()
         #login sukses
         #generatetoken
         token = jwt.encode(
            {
               "username":queryUsername,
               "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
            },app.config['SECRET_KEY'] ,algorithm='HS256')
         return make_response(jsonify({'message':'Login Berhasil',
                                       'data':
                                          {
                                             'name':querydata.name,
                                             'username':querydata.username,
                                             'email':querydata.email,
                                             'token':token,
                                             }
                                          }),{'code': 200})
      #login gagal
      return make_response(jsonify({'msg':'Login Gagal'}), 404)
   
class getAllUser(Resource):
   def get(self):
      dataquery = UserModel.query.all()
      output = [
         {
            "id":data.id,
            "username":data.username,
            "email":data.email,
            "password":data.password
         } for data in dataquery
                ]
      return make_response(jsonify(output),200)

class getAllUserByID(Resource):
   def get(self,id):
      dataquery = UserModel.query.get(id)
      if dataquery :
         return make_response(jsonify({"username": dataquery.username, "email": dataquery.email, "password": dataquery.password}),200)
      return make_response(jsonify({'msg':'User dengan id : ' +  id +  ' tidak ada'}),404)
      
#inisialisai resource api
api.add_resource(Register,"/api/register",methods=['POST'])
api.add_resource(Login,"/api/login",methods=['POST'])
api.add_resource(getAllUser,"/api/users",methods=['GET'])
api.add_resource(getAllUserByID,"/api/user/<id>",methods=['GET'])












@app.route('/')
def home():
  return render_template("index.html")

@app.route('/tarif')
def tariftol():
   return render_template("tariftol.html")

@app.route('/restarea')
def restarea():
   return render_template("restarea.html")
@app.route('/contact')
def callcenter():
   return render_template("contact.html")










if __name__ == '__main__':

    app.run(debug=True)