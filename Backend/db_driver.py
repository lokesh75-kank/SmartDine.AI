import sqlite3
from typing import Optional, List
from dataclasses import dataclass
from contextlib import contextmanager
from datetime import datetime

@dataclass
class Booking:
    name: str
    phonenumber: str
    numberofpeople: str
    dateandtime: str
    specialrequest: str

class DatabaseDriver:
    def __init__(self, db_path: str = "restaurant_db.sqlite"):
        self.db_path = db_path
        self._init_db()
        
    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
            
    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bookings (
                    name TEXT PRIMARY KEY,
                    phonenumber TEXT NOT NULL,
                    numberofpeople TEXT NOT NULL,
                    dateandtime TEXT NOT NULL,
                    specialrequest TEXT
                )
            """)
            conn.commit()
            
    # CREATE
    def create_booking(self, name: str, phonenumber: str, numberofpeople: str, 
                      dateandtime: str, specialrequest: str) -> Optional[Booking]:
        """Create a new booking"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """INSERT INTO bookings 
                       (name, phonenumber, numberofpeople, dateandtime, specialrequest) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (name, phonenumber, numberofpeople, dateandtime, specialrequest)
                )
                conn.commit()
                return Booking(name=name, phonenumber=phonenumber, 
                             numberofpeople=numberofpeople, dateandtime=dateandtime,
                             specialrequest=specialrequest)
            except sqlite3.IntegrityError:
                return None
    
    # READ
    def get_booking_by_name(self, name: str) -> Optional[Booking]:
        """Retrieve a booking by name"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM bookings WHERE name = ?", (name,))
            row = cursor.fetchone()
            if not row:
                return None
            
            return Booking(
                name=row[0],
                phonenumber=row[1],
                numberofpeople=row[2],
                dateandtime=row[3],
                specialrequest=row[4]
            )
    
    def get_all_bookings(self) -> List[Booking]:
        """Retrieve all bookings"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM bookings")
            rows = cursor.fetchall()
            
            return [Booking(
                name=row[0],
                phonenumber=row[1],
                numberofpeople=row[2],
                dateandtime=row[3],
                specialrequest=row[4]
            ) for row in rows]
    
    def get_bookings_by_date(self, date: str) -> List[Booking]:
        """Retrieve all bookings for a specific date"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM bookings WHERE date(dateandtime) = date(?)",
                (date,)
            )
            rows = cursor.fetchall()
            
            return [Booking(
                name=row[0],
                phonenumber=row[1],
                numberofpeople=row[2],
                dateandtime=row[3],
                specialrequest=row[4]
            ) for row in rows]
    
    # UPDATE
    def update_booking(self, name: str, **kwargs) -> Optional[Booking]:
        """Update an existing booking"""
        valid_fields = {'phonenumber', 'numberofpeople', 'dateandtime', 'specialrequest'}
        update_fields = {k: v for k, v in kwargs.items() if k in valid_fields and v is not None}
        
        if not update_fields:
            return None
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Build the UPDATE query dynamically
            query = "UPDATE bookings SET " + ", ".join(f"{k} = ?" for k in update_fields)
            query += " WHERE name = ?"
            
            values = list(update_fields.values()) + [name]
            
            cursor.execute(query, values)
            conn.commit()
            
            if cursor.rowcount == 0:
                return None
                
            return self.get_booking_by_name(name)
    
    # DELETE
    def delete_booking(self, name: str) -> bool:
        """Delete a booking by name"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM bookings WHERE name = ?", (name,))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_all_bookings(self) -> int:
        """Delete all bookings and return the number of deleted records"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM bookings")
            conn.commit()
            return cursor.rowcount
    
    # UTILITY METHODS
    def count_bookings(self) -> int:
        """Count total number of bookings"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM bookings")
            return cursor.fetchone()[0]
    
    def exists_booking(self, name: str) -> bool:
        """Check if a booking exists"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM bookings WHERE name = ?", (name,))
            return cursor.fetchone() is not None


