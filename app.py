import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, reqparse, inputs, fields, marshal_with
import sys

app = Flask(__name__)
api = Api(app)
parser = reqparse.RequestParser()
parser2 = reqparse.RequestParser()
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///calendar.db"

# JSON Serialized Fields
resource_fields = {
        "id": fields.Integer,
        "event": fields.String,
        "date": fields.DateTime(dt_format='iso8601')
}


# Database Model
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String, nullable=False)
    date = db.Column(db.Date, nullable=False)


db.create_all()


# Resources
class EventsToday(Resource):
    @marshal_with(resource_fields)
    def get(self):
        events = Event.query.filter(Event.date == datetime.date.today()).all()
        return events, 200


class Events(Resource):
    parser.add_argument(
        "event",
        type=str,
        help="The event name is required!",
        required=True
    )
    parser.add_argument(
        "date",
        type=inputs.date,
        help="The event date with the correct format is required! The correct format is YYYY-MM-DD!",
        required=True
    )
    parser2.add_argument("start_time", type=inputs.date)
    parser2.add_argument("end_time", type=inputs.date)

    def post(self):
        args = parser.parse_args()
        events = Event(event=args['event'], date=args['date'].date())
        db.session.add(events)
        db.session.commit()
        response = {
            "message": "The event has been added!",
            "event": args['event'],
            "date": str(args['date'].date())
        }
        return response, 200

    @marshal_with(resource_fields)
    def get(self):
        args = parser2.parse_args()
        events = Event.query.all()
        if args['start_time'] and args['end_time']:
            events = Event.query.filter(Event.date.between(args['start_time'], args['end_time'])).all()
        return events, 200


class EventByID(Resource):
    @marshal_with(resource_fields)
    def get(self, id):
        events = Event.query.get_or_404(id, "The event doesn't exist!")
        return events, 200

    def delete(self, id):
        events = Event.query.get_or_404(id, "The event doesn't exist!")
        db.session.delete(events)
        db.session.commit()
        return {"message": "The event has been deleted!"}


# Endpoints
api.add_resource(EventsToday, "/event/today")
api.add_resource(Events, "/event")
api.add_resource(EventByID, "/event/<int:id>")

# do not change the way you run the program
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
