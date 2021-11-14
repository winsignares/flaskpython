from flask import Flask,render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/prueba'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# settings
app.secret_key = "william"

#trabajamos con la bd 
db = SQLAlchemy(app)

ma = Marshmallow(app)

#Creamos los modelos a trabajar#

class Articulo(db.Model):
    __tablename__ = 'Articulo'
    id = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(70), unique=True)
    Precio = db.Column(db.Float())

    def __init__(self, Nombre, Precio):
        self.Nombre = Nombre
        self.Precio = Precio
db.create_all()

class ArticulosSchema(ma.Schema):
    class Meta:
        fields = ('id', 'Nombre', 'Precio')

class Pedido(db.Model):
    __tablename__ = 'Pedido'
    id = db.Column(db.Integer, primary_key=True)
    NombrePersona = db.Column(db.String(70), unique=True)
    Direccion = db.Column(db.String(70))
    Estado = db.Column(db.String(70))
    #creamos la relación#
    Id_Articulos = db.Column(db.Integer, db.ForeignKey('Articulo.id'))
    Articulo = db.relationship('Articulo', backref=db.backref('pedidos', lazy=True))

    def __init__(self, NombrePersona, Direccion,Id_Articulos,Estado):
        self.NombrePersona = NombrePersona
        self.Direccion = Direccion
        self.Id_Articulos = Id_Articulos
        self.Estado = Estado
        #self.Articulo = Articulo
        

class PedidosSchema(ma.Schema):
    class Meta:
        fields = ('id', 'NombrePersona', 'Direccion','Id_Articulos','Estado')

db.create_all()

class ResultdadosSchema(ma.Schema):
    class Meta:
        fields = ('id', 'NombrePersona', 'Direccion','Id_Articulos')

articulo_schema = ArticulosSchema()
articulos_schema = ArticulosSchema(many=True)
pedido_schema = PedidosSchema()
pedidos_schema = PedidosSchema(many=True)

#Articulos#
@app.route('/Articulo', methods=['GET'])
def indexArticulo():
    all_articulos = Articulo.query.all()
    resultArticulo = articulos_schema.dump(all_articulos)
    return render_template("Articulos/index.html",  articulos =resultArticulo)

@app.route('/addArticulo', methods=['GET','POST'])
def addArticulo(): 
    if request.method == 'POST':
        Nombre = request.form['Nombre']
        Precio = request.form['Precio']
        newArticulo= Articulo(Nombre, Precio)
        db.session.add(newArticulo)
        db.session.commit()
        flash('Agregado con Exito')
        return redirect(url_for('index'))

 
@app.route('/', methods=['GET'])
def index():
    all_pedidos = Pedido.query.all()
    result = pedidos_schema.dump(all_pedidos)
    cruce= db.session.query(Pedido, Articulo).join(Articulo).all()
    #join con 3 tablas 
    # cruce= db.session.query(Tabla1, Tablaintermedia, Tabla2). \ select_from(Tabla1).join(TablaIntermedia).join(Tabla2).all()
    all_articulos = Articulo.query.all()
    resultArticulo = articulos_schema.dump(all_articulos)
    return render_template("body.html", pedidos = result, articulos =resultArticulo, resultados = cruce)


#Pedidos  
@app.route('/add', methods=['GET','POST'])
def add():
 
    if request.method == 'POST':
        NombrePersona = request.form['NombrePersona']
        Direccion = request.form['Direccion']
        Id_Articulos = request.form.get('IdArticulos')
        Estado = "En proceso"
        newpedido= Pedido(NombrePersona, Direccion, Id_Articulos,Estado)
        db.session.add(newpedido)
        db.session.commit()
        flash('Agregado con Exito')
        return redirect(url_for('index'))

@app.route('/cambioE/<id>', methods = ['POST', 'GET'])
def getPedido(id):
    if request.method == 'GET':
        pedido = Pedido.query.get(id)               
        
        if pedido.Estado == "En proceso":
            pedido.Estado =  "Repartido"
            db.session.commit()        
            flash('Actualizado con Exito')
            return redirect(url_for('index'))
        elif pedido.Estado ==  "Repartido":
            pedido.Estado =  "Terminado"
            db.session.commit()        
            flash('Actualizado con Exito')
            return redirect(url_for('index'))
        else:
            return redirect(url_for('index'))
        #all_articulos = Articulo.query.all()
        #resultArticulo = articulos_schema.dump(all_articulos)      
        #return render_template('edit.html', articulos =resultArticulo, pedido= pedido)
        #return pedido.Estado


#Articulos

@app.route('/editArticulo/<id>', methods = ['POST', 'GET'])
def get_Articulo(id):
    if request.method == 'GET':
      articulo = Articulo.query.get(id)      
      return render_template('Articulos/edit.html', articulo= articulo)

@app.route('/updateArticulo/<id>', methods=['POST'])
def updateArticulo(id):
    if request.method == 'POST':
        Nombre = request.form['Nombre']
        Precio = request.form['Precio'] 
        articulo = Articulo.query.get(id)
        articulo.Nombre = Nombre
        articulo.Precio = Precio
        db.session.commit()        
        flash('Actualizado con Exito')
        return redirect(url_for('index'))

@app.route('/deleteArticulo/<string:id>', methods = ['POST','GET'])
def deleteArticulo(id):
    articulo = Articulo.query.get(id)
    db.session.delete(articulo)
    db.session.commit()
    flash('Eliminado con Exito')
    return redirect(url_for('index'))


'''
API
''' 
@app.route('/allarticulo', methods=['GET'])
def indexApi():
    all_articulos = Articulo.query.all()
    resultArticulo = articulos_schema.dump(all_articulos)
    return jsonify(resultArticulo)


#Iniciamos app para que se ejecute en un puerto#
if __name__ == "__main__":
    app.run(debug=True)
