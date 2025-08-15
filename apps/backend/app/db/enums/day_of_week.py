"""
Enumerations for day of week.
"""

from enum import IntEnum

class DayOfWeek(IntEnum):
    """
    Enumeration for days of the week.
    
    Values follow ISO 8601 standard:
    Monday = 1, Tuesday = 2, ..., Sunday = 7
    """
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7

    @classmethod
    def get_display_name(cls, day: int) -> str:
        """Get human-readable name for a day."""
        names = {
            1: "Lunes",
            2: "Martes", 
            3: "Miércoles",
            4: "Jueves",
            5: "Viernes",
            6: "Sábado",
            7: "Domingo"
        }
        return names.get(day, f"Día {day}")
    
    @classmethod
    def get_short_name(cls, day: int) -> str:
        """Get short name for a day."""
        names = {
            1: "LUN",
            2: "MAR",
            3: "MIE", 
            4: "JUE",
            5: "VIE",
            6: "SAB",
            7: "DOM"
        }
        return names.get(day, f"D{day}")