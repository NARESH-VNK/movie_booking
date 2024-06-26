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
