from livekit.agents import llm
import enum
from typing import Annotated
import logging
from db_driver import DatabaseDriver, Booking
from datetime import datetime
import sqlite3

logger = logging.getLogger("booking-data")
logger.setLevel(logging.INFO)

DB = DatabaseDriver()

class BookingDetails(enum.Enum):
    Name = "name"
    PhoneNumber = "phonenumber"
    NumberOfPeople = "numberofpeople"
    DateAndTime = "dateandtime"
    SpecialRequest = "specialrequest"

class AssistantFnc(llm.FunctionContext):
    def __init__(self):
        super().__init__()
        self._booking_details = {
            BookingDetails.Name: "",
            BookingDetails.PhoneNumber: "",
            BookingDetails.NumberOfPeople: "",
            BookingDetails.DateAndTime: "",
            BookingDetails.SpecialRequest: ""
        }
    
    def _format_booking(self, booking: Booking) -> str:
        """Format a booking into a readable string"""
        return (f"Name: {booking.name}\n"
                f"Date and Time: {booking.dateandtime}\n"
                f"Number of people: {booking.numberofpeople}\n"
                f"Phone: {booking.phonenumber}\n"
                f"Special requests: {booking.specialrequest or 'None'}")

    def _is_same_day(self, date1_str: str, date2_str: str) -> bool:
        """Compare if two dates are on the same day"""
        date1 = datetime.strptime(date1_str, "%Y-%m-%d %H:%M")
        date2 = datetime.strptime(date2_str, "%Y-%m-%d %H:%M")
        return date1.date() == date2.date()
    
    @llm.ai_callable(description="create a new restaurant booking")
    def create_booking(
        self,
        name: Annotated[str, llm.TypeInfo(description="Customer's full name")],
        phonenumber: Annotated[str, llm.TypeInfo(description="Customer's phone number")],
        numberofpeople: Annotated[str, llm.TypeInfo(description="Number of people in the party")],
        dateandtime: Annotated[str, llm.TypeInfo(description="Date and time of the booking (format: YYYY-MM-DD HH:MM)")],
        specialrequest: Annotated[str, llm.TypeInfo(description="Any special requests or dietary requirements")] = ""
    ):
        logger.info("creating booking for name: %s", name)
        
        # Validate inputs
        try:
            booking_datetime = datetime.strptime(dateandtime, "%Y-%m-%d %H:%M")
            if booking_datetime < datetime.now():
                return "Sorry, you cannot book for a past date and time."
        except ValueError:
            return "Invalid date format. Please use YYYY-MM-DD HH:MM format"
        
        if not phonenumber.replace("+", "").replace("-", "").replace(" ", "").isdigit():
            return "Invalid phone number format"
        
        if not numberofpeople.isdigit() or int(numberofpeople) < 1:
            return "Invalid number of people"
        
        try:
            result = DB.create_booking(
                name=name,
                phonenumber=phonenumber,
                numberofpeople=numberofpeople,
                dateandtime=dateandtime,
                specialrequest=specialrequest
            )
            
            if result:
                return f"Booking confirmed!\n{self._format_booking(result)}"
            else:
                return "A booking with this name already exists"
            
        except Exception as e:
            logger.error("Error creating booking: %s", str(e))
            return "Failed to create booking. Please try again"
    
    @llm.ai_callable(description="view booking details")
    def view_booking(
        self,
        name: Annotated[str, llm.TypeInfo(description="Customer's full name")]
    ):
        """View details of a specific booking"""
        logger.info("viewing booking for name: %s", name)
        
        result = DB.get_booking_by_name(name)
        if result is None:
            return "No booking found under this name"
        
        return f"Found booking:\n{self._format_booking(result)}"
    
    @llm.ai_callable(description="update an existing booking")
    def update_booking(
        self,
        name: Annotated[str, llm.TypeInfo(description="Customer's full name")],
        phonenumber: Annotated[str, llm.TypeInfo(description="New phone number")] = None,
        numberofpeople: Annotated[str, llm.TypeInfo(description="New number of people")] = None,
        dateandtime: Annotated[str, llm.TypeInfo(description="New date and time (YYYY-MM-DD HH:MM)")] = None,
        specialrequest: Annotated[str, llm.TypeInfo(description="New special requests")] = None
    ):
        """Update an existing booking"""
        logger.info("updating booking for name: %s", name)
        
        # Verify booking exists
        if not DB.exists_booking(name):
            return "No booking found under this name"
        
        # Validate date if provided
        if dateandtime:
            try:
                booking_datetime = datetime.strptime(dateandtime, "%Y-%m-%d %H:%M")
                if booking_datetime < datetime.now():
                    return "Sorry, you cannot book for a past date and time."
            except ValueError:
                return "Invalid date format. Please use YYYY-MM-DD HH:MM format"
        
        # Validate phone number if provided
        if phonenumber and not phonenumber.replace("+", "").replace("-", "").replace(" ", "").isdigit():
            return "Invalid phone number format"
        
        # Validate number of people if provided
        if numberofpeople and (not numberofpeople.isdigit() or int(numberofpeople) < 1):
            return "Invalid number of people"
        
        # Update booking
        update_data = {}
        if phonenumber: update_data['phonenumber'] = phonenumber
        if numberofpeople: update_data['numberofpeople'] = numberofpeople
        if dateandtime: update_data['dateandtime'] = dateandtime
        if specialrequest is not None: update_data['specialrequest'] = specialrequest
        
        result = DB.update_booking(name, **update_data)
        if result:
            return f"Booking updated successfully!\n{self._format_booking(result)}"
        return "Failed to update booking"
    
    @llm.ai_callable(description="cancel a booking")
    def cancel_booking(
        self,
        name: Annotated[str, llm.TypeInfo(description="Customer's full name")]
    ):
        """Cancel/delete a booking"""
        logger.info("canceling booking for name: %s", name)
        
        if DB.delete_booking(name):
            return f"Booking for {name} has been cancelled"
        return "No booking found under this name"
    
    @llm.ai_callable(description="view all bookings for a specific date")
    def view_bookings_by_date(
        self,
        date: Annotated[str, llm.TypeInfo(description="Date to check bookings for (YYYY-MM-DD)")]
    ):
        """View all bookings for a specific date"""
        logger.info("viewing bookings for date: %s", date)
        
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return "Invalid date format. Please use YYYY-MM-DD format"
        
        bookings = DB.get_bookings_by_date(date)
        if not bookings:
            return f"No bookings found for {date}"
        
        response = f"Bookings for {date}:\n\n"
        for booking in bookings:
            response += self._format_booking(booking) + "\n\n"
        return response


