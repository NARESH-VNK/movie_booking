from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.json_util import dumps
import Movie as mv
import User
import Booking
import MovieTicketBookingSystem


app = Flask(__name__)

# username = 'flaskuser'
# password = 'flaskuser'
# clustername = 'newc'
# database_name = 'db'

# Configuration for MongoDB
app.config["MONGO_URI"] = "mongodb+srv://flaskuser:flaskuser@newc.3ow5cor.mongodb.net/db?retryWrites=true&w=majority"
mongo = PyMongo(app)


# Initialize the booking system
system =MovieTicketBookingSystem.MovieTicketBookingSystem()

@app.route('/movies', methods=['GET'])
def get_movies():
    return jsonify(system.get_movies())

@app.route('/book', methods=['POST'])
def book_ticket():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    movie_name = data.get('movie_name')
    number_of_seats = data.get('number_of_seats')

    if not all([name, email, movie_name, number_of_seats]):
        return jsonify({"message": "Missing required fields"}), 400

    user = User.User(name, email)
    result = system.book_ticket(user, movie_name, number_of_seats)
    return jsonify(result)


@app.route('/user/seats', methods=['PUT'])
def update_user_seats():
    data = request.json
    email = data.get('email')
    movie_name = data.get('movie_name')
    new_number_of_seats = data.get('new_number_of_seats')

    if not all([email, movie_name, new_number_of_seats]):
        return jsonify({"message": "Missing required fields"}), 400

    result = system.update_user_seats(email, movie_name, new_number_of_seats)
    return jsonify(result)


@app.route('/booking', methods=['DELETE'])
def delete_booking():
    data = request.json
    email = data.get('email')
    movie_name = data.get('movie_name')
    booking_id = data.get('booking_id')

    if not all([email, movie_name, booking_id]):
        return jsonify({"message": "Missing required fields"}), 400

    result = system.delete_booking(email, movie_name, booking_id)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
