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

api = Api(app=app)


@app.route("/")
def home():
    return ""


class Campers(Resource):
    def get(self):
        campers = [camper.to_dict(rules=("-signups",)) for camper in Camper.query.all()]

        return make_response(campers, 200)

    def post(self):
        # request = request.get_json()
        try:
            new_camper = Camper(name=request.json["name"], age=request.json["age"])
            db.session.add(new_camper)
            db.session.commit()

            return new_camper.to_dict(rules=("-signups",)), 201
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)


api.add_resource(Campers, "/campers")


class CampersById(Resource):
    def get(self, id):
        camper = Camper.query.filter(Camper.id == id).one_or_none()
        if camper is None:
            return make_response({"error": "Camper not found"}, 404)

        return make_response(camper.to_dict(), 200)

    def patch(self, id):
        camper = Camper.query.get(id)
        if not camper:
            return make_response({"error": "Camper not found"}, 404)
        data = request.get_json()
        try:
            setattr(camper, "name", data["name"])
            setattr(camper, "age", data["age"])
            db.session.add(camper)
            db.session.commit()

            return camper.to_dict(rules=("-signups",)), 202

        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)


api.add_resource(CampersById, "/campers/<int:id>")


class Activities(Resource):
    def get(self):
        activities = Activity.query.all()
        activities_data = [
            {
                "id": activity.id,
                "name": activity.name,
                "difficulty": activity.difficulty,
            }
            for activity in activities
        ]
        return make_response(jsonify(activities_data), 200)


api.add_resource(Activities, "/activities")


class ActivititesById(Resource):
    def delete(self, id):
        activity = Activity.query.filter_by(id=id).one_or_none()

        if activity:
            db.session.delete(activity)
            db.session.commit()

            return make_response({}, 204)

        return make_response({"error": "Activity not found"}, 404)


api.add_resource(ActivititesById, "/activities/<int:id>")


class Signups(Resource):
    def post(self):
        try:
            signup = Signup(
                time=request.json["time"],
                camper_id=request.json["camper_id"],
                activity_id=request.json["activity_id"],
            )

            db.session.add(signup)
            db.session.commit()

            return make_response(signup.to_dict(), 201)

        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)


api.add_resource(Signups, "/signups")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
