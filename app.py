from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.json_util import dumps

app = Flask(__name__)

# username = 'flaskuser'
# password = 'flaskuser'
# clustername = 'newc'
# database_name = 'db'

# Configuration for MongoDB
app.config["MONGO_URI"] = "mongodb+srv://flaskuser:flaskuser@newc.3ow5cor.mongodb.net/db?retryWrites=true&w=majority"
mongo = PyMongo(app)

class Movie:
    def __init__(self, title):
        self.title = title
        self.available_seats = 100

    def book_seat(self, number_of_seats):
        if self.available_seats >= number_of_seats:
            self.available_seats -= number_of_seats
            return True
        else:
            return False

    def release_seat(self, number_of_seats):
        self.available_seats += number_of_seats

class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

class Booking:
    def __init__(self, booking_id, user, movie, number_of_seats):
        self.booking_id = booking_id
        self.user = user
        self.movie = movie
        self.number_of_seats = number_of_seats

    def confirm_booking(self):
        if self.movie.book_seat(self.number_of_seats):
            return {
                "status": "success",
                "message": "Booking confirmed",
                "details": {
                    "booking_id": self.booking_id,
                    "user": {"name": self.user.name, "email": self.user.email},
                    "movie": self.movie.title,
                    "number_of_seats": self.number_of_seats,
                    "seats_remaining": self.movie.available_seats
                }
            }
        else:
            return {
                "status": "failure",
                "message": "Booking failed. No available seats."
            }

class MovieTicketBookingSystem:
    def __init__(self):
        self.movies = [
            Movie("kgf1"),
            Movie("kgf2"),
            Movie("kgf3"),
            Movie("kgf4")
        ]
        self.bookings = {}
        self.next_booking_id = 1
        
            
    def get_movies(self):
        return [{"title": movie.title, "available_seats": movie.available_seats} for movie in self.movies]

    def book_ticket(self, user, movie_name, number_of_seats):
        movie = next((movie for movie in self.movies if movie.title == movie_name), None)
        if movie:
            booking = Booking(self.next_booking_id, user, movie, number_of_seats)
            result = booking.confirm_booking()
            if result["status"] == "success":
                # Save booking to MongoDB
                booking_record = {
                    "booking_id": self.next_booking_id,
                    "user": {"name": user.name, "email": user.email},
                    "movie": movie.title,
                    "number_of_seats": number_of_seats
                }
                mongo.db.bookings.insert_one(booking_record)
                self.bookings[self.next_booking_id] = booking
                self.next_booking_id += 1
            return result
        else:
            return {"message": "Invalid movie selection."}


    def update_user_seats(self, email, movie_name, new_number_of_seats):
        if new_number_of_seats <= 0:
            return {"message": "Number of seats must be higher than zero."}

        updated_bookings = []
        for booking in self.bookings.values():
            if booking.user.email == email and booking.movie.title == movie_name:
                if booking.movie.available_seats + booking.number_of_seats >= new_number_of_seats:
                    booking.movie.release_seat(booking.number_of_seats)
                    booking.number_of_seats = new_number_of_seats
                    booking.movie.book_seat(new_number_of_seats)
                    updated_bookings.append(booking.booking_id)
                else:
                    return {"message": "Not enough available seats to update the booking."}

        if updated_bookings:
            return {"message": "Bookings updated successfully.", "updated_bookings": updated_bookings}
        else:
            return {"message": "User not found or no bookings for the specified movie."}

        
    def delete_booking(self, email, movie_name, booking_id):
        if booking_id in self.bookings:
            booking = self.bookings[booking_id]
            if booking.user.email == email and booking.movie.title == movie_name:
                booking.movie.release_seat(booking.number_of_seats)
                del self.bookings[booking_id]          
                # Delete booking from MongoDB
                mongo.db.bookings.delete_one({"booking_id": booking_id, "user.email": email, "movie": movie_name})
                return {"message": "Booking deleted successfully."}
            else:
                return {"message": "Email or movie name does not match the booking."}
        else:
            return {"message": "Booking not found."}


# Initialize the booking system
system = MovieTicketBookingSystem()

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

    user = User(name, email)
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
