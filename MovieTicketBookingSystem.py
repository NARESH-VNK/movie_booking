import Movie as mv
import Booking



class MovieTicketBookingSystem:
    def __init__(self):
        self.movies = [
            mv.Movie("kgf1"),
            mv.Movie("kgf2"),
            mv.Movie("kgf3"),
            mv.Movie("kgf4")
        ]
        self.bookings = {}
        self.next_booking_id = 1
        
            
    def get_movies(self):
        return [{"title": movie.title, "available_seats": movie.available_seats} for movie in self.movies]

    def book_ticket(self, user, movie_name, number_of_seats):
        movie = next((movie for movie in self.movies if movie.title == movie_name), None)
        if movie:
            booking = Booking.Booking(self.next_booking_id, user, movie, number_of_seats)
            result = booking.confirm_booking()
            if result["status"] == "success":
                # Save booking to MongoDB
                booking_record = {
                    "booking_id": self.next_booking_id,
                    "user": {"name": user.name, "email": user.email},
                    "movie": movie.title,
                    "number_of_seats": number_of_seats
                }
                from app import mongo
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
                from app import mongo
                mongo.db.bookings.delete_one({"booking_id": booking_id, "user.email": email, "movie": movie_name})
                return {"message": "Booking deleted successfully."}
            else:
                return {"message": "Email or movie name does not match the booking."}
        else:
            return {"message": "Booking not found."}