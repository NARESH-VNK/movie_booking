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