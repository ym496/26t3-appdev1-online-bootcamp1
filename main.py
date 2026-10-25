from flask import Flask, session
from application.models import db, User

app = Flask(__name__)
app.secret_key = 'mujic-streaming' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///beatbox.db'
db.init_app(app)



def init_db():
    with app.app_context():
        import application.controllers
        db.create_all()
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin', password='admin', role='admin')
            db.session.add(admin_user)
            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=True)