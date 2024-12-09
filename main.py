from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, NumberRange
import requests
from dotenv import load_dotenv
from os import environ
from datetime import datetime
from typing import Optional

load_dotenv()
ID = environ["ID"]
SECRET = environ["SECRET"]
TOKEN = environ["TOKEN"]
print(ID, SECRET)

class Base(DeclarativeBase):
    pass

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_top_videogames.db'

Bootstrap5(app)

db = SQLAlchemy(model_class=Base)
db.init_app(app=app)

# CREATE DB
class TopVideogames(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title : Mapped[str] = mapped_column(String(100), unique=True)
    year: Mapped[int] = mapped_column(Integer())
    description: Mapped[str] = mapped_column(String(1000))
    rating: Mapped[float] = mapped_column(Float())
    ranking: Mapped[Optional[int]] = mapped_column(Integer())
    review: Mapped[Optional[str]] = mapped_column(String(250))
    img_url: Mapped[str] = mapped_column(String(100))

    def __repr__(self):
        return f'Videogame {self.title} ({self.year})'

with app.app_context():
    db.create_all()

# CREATE EDIT FORM
class EditForm(FlaskForm):
    ranking = IntegerField(label='Rank from 0 to 10', validators=[DataRequired(), NumberRange(min=0, max=10)])
    review = StringField(label='Review the videogame', validators=[])
    submit = SubmitField(label='Submit')

# CREATE ADD FORM
class AddForm(FlaskForm):
    title = StringField(label='Choose a videogame title', validators=[DataRequired()])
    submit = SubmitField(label='Submit')

# DEFINE USEFUL FUNCTIONS
def call_game_api(name):
    # If there is no authentication token yet, write this on the console:
    # response = requests.post(url='https://id.twitch.tv/oauth2/token', data={'client_id': '77xg375rmm8qhbnrnrp9rpcgfkhbfg', 'client_secret': 'ty82mz7rd4eb8ygh3hzlczvkvs8ds4', 'grant_type': 'client_credentials'})

    HEADER = {
        'Client-ID': ID,
        'Authorization': f'Bearer {TOKEN}'
    }
    BODY = f'fields id, name, created_at; search "{name}"; limit: 100;'

    response = requests.post(url='https://api.igdb.com/v4/games', headers=HEADER, data=BODY)
    return response.json()

def find_game_details(_id):
    HEADER = {
        'Client-ID': ID,
        'Authorization': f'Bearer {TOKEN}'
    }
    BODY_DETAILS = f'fields name, created_at, rating, cover, summary; where id = {_id};'
    COVER_DETAILS = f'fields url; where game = {_id};'

    details_response = requests.post(url='https://api.igdb.com/v4/games', headers=HEADER, data=BODY_DETAILS)
    cover_response = requests.post(url='https://api.igdb.com/v4/covers', headers=HEADER, data=COVER_DETAILS)

    return details_response.json(), cover_response.json()

@app.route("/")
def home():
    results = db.session.execute(db.select(TopVideogames).order_by(TopVideogames.ranking)).scalars()
    all_videogames = [result for result in results]
    return render_template("index.html", all_videogames=all_videogames)

@app.route("/edit/<int:_id>", methods=["GET", "POST"])
def edit(_id):
    form = EditForm()
    videogame = db.session.execute(db.select(TopVideogames).where(TopVideogames.id == _id)).scalar()
    if form.is_submitted():
        print("submitted")
    if form.validate():
        print("Valid")
    if form.validate_on_submit():
        new_ranking = form.ranking.data
        new_review = form.review.data
        print(new_ranking)
        videogame_to_update = db.session.execute(db.select(TopVideogames).where(TopVideogames.id == _id)).scalar()
        print(videogame_to_update, videogame_to_update.title)
        videogame_to_update.ranking = new_ranking
        if new_review:
            videogame_to_update.review = new_review
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", form=form, videogame=videogame)

@app.route("/delete/<int:_id>")
def delete(_id):
    videogame_to_delete = db.session.execute(db.select(TopVideogames).where(TopVideogames.id == _id)).scalar()
    db.session.delete(videogame_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/add", methods=["GET", "POST"])
def add():
    form = AddForm()
    if form.is_submitted():
        print("submitted")
    if form.validate():
        print("Valid")
    if form.validate_on_submit():
        search_title = form.title.data
        response = call_game_api(search_title)
        videogame_list = [(videogame['name'], datetime.fromtimestamp(videogame['created_at']).year, videogame['id']) for videogame in response]
        print(videogame_list)
        return render_template('select.html', videogame_list=videogame_list)

    return render_template('add.html', form=form)

@app.route("/select/<int:_id>")
def select(_id):
    details, cover_url = find_game_details(_id)
    print(details)
    print(cover_url)
    new_entry = TopVideogames(
        title=details[0]['name'],
        year=datetime.fromtimestamp(details[0]['created_at']).year,
        description=details[0]['summary'],
        rating=round(details[0]['rating'], 2),
        img_url=cover_url[0]['url']
    )
    db.session.add(new_entry)
    db.session.commit()

    db_instance = db.session.execute(db.select(TopVideogames).where(TopVideogames.title == details[0]['name'])).scalar()
    return redirect(url_for('edit', _id=db_instance.id))


# USE THIS API
# https://www.igdb.com/api


if __name__ == '__main__':
    app.run(debug=True)
    db.session.close()

















# CREATE TABLE
# new_videogame_1 = TopVideogames(
#     title="Mario and Luigi: Superstar Saga",
#     year=2003,
#     genre= "RPG",
#     description="Travel to the Beanbean Kingdom with Mario and Luigi to recover Princess Peach's stolen voice in this humorous RPG",
#     rating=9.0,
#     ranking=9,
#     review="A very funny game!",
#     img_url="https://assets-prd.ignimgs.com/2022/01/31/mario-and-luigi-superstar-saga-button-crop-1643611937386.jpg"
# )

# new_videogame_2 = TopVideogames(
#     title="Pokemon Soul Silver",
#     year=2010,
#     genre= "RPG",
#     description="Explore the Johto and Kanto regions, capturing and training Pokémon to become the ultimate Pokémon Trainer",
#     rating=8.7,
#     ranking=10,
#     review="The perfect pokemon game!",
#     img_url="https://assets1.ignimgs.com/2019/05/17/pokemon-soulsilver---button-1558057647951.jpg"
# )

# with app.app_context():
#     db.create_all()
#     db.session.add(new_videogame_1)
#     db.session.add(new_videogame_2)
#     db.session.commit()
#     db.session.close()
