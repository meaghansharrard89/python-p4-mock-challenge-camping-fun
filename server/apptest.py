#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def home():
    return ""


class Campers(Resource):
    def get(self):
        campers = [
            camper.to_dict(
                only=(
                    "id",
                    "name",
                    "age",
                )
            )
            for camper in Camper.query.all()
        ]
        return make_response(campers, 200)

    def post(self):
        data = request.get_json()
        camper = Camper()
        try:
            camper.name = data.get("name")
            camper.age = data.get("age")
            db.session.add(camper)
            db.session.commit()
            return make_response(
                camper.to_dict(
                    only=(
                        "id",
                        "name",
                        "age",
                    )
                ),
                201,
            )
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)


api.add_resource(Campers, "/campers")


class CampersById(Resource):
    def get(self, id):
        camper = Camper.query.filter(Camper.id == id).first()
        if camper is None:
            return make_response({"error": "Camper not found"}, 404)
        return make_response(camper.to_dict(), 200)

    def patch(self, id):
        camper = Camper.query.filter(Camper.id == id).first()
        if not camper:
            return make_response({"error": "Camper not found"}, 404)
        data = request.get_json()
        try:
            setattr(camper, "name", data["name"])
            setattr(camper, "age", data["age"])
            db.session.add(camper)
            db.session.commit()
            return (
                camper.to_dict(
                    only=(
                        "id",
                        "name",
                        "age",
                    )
                ),
                202,
            )
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)


api.add_resource(CampersById, "/campers/<int:id>")


class Activities(Resource):
    def get(self):
        activities = [
            activity.to_dict(
                only=(
                    "id",
                    "name",
                    "difficulty",
                )
            )
            for activity in Activity.query.all()
        ]
        return make_response(activities, 200)


api.add_resource(Activities, "/activities/<int:id>")


class ActivitiesById(Resource):
    def delete(self, id):
        activity = Activity.query.filter(Activity.id == id).first()
        if activity:
            db.session.delete(activity)
            db.session.commit()
            return make_response({}, 204)
        return make_response({"error": "Activity not found"}, 404)


api.add_resource(ActivitiesById, "/activities/<int:id>")


class Signups(Resource):
    def post(self):
        data = request.get_json()
        signup = Signup()
        try:
            signup.camper_id = data.get("camper_id")
            signup.activity_id = data.get("activity_id")
            signup.time = data.get("time")
            db.session.add(signup)
            db.session.commit()
            return make_response(signup.to_dict(), 201)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)


api.add_resource(Signups, "/signups")


if __name__ == "__main__":
    app.run(port=5555, debug=True)
