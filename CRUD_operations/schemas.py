
from pydantic import BaseModel
from typing import Optional


class CrimeRecord(BaseModel):
    case_number: str

    date: Optional[str] = None
    block: Optional[str] = None
    iucr_code: Optional[str] = None
    location_desc: Optional[str] = None
    arrest: Optional[str] = None
    domestic: Optional[str] = None
    beat_num: Optional[str] = None
    district_code: Optional[str] = None
    ward_no: Optional[int] = None
    community_code: Optional[str] = None
    fbi_code: Optional[str] = None
    x_coordinate: Optional[float] = None
    y_coordinate: Optional[float] = None
    year: Optional[int] = None
    date_of_update: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location: Optional[str] = None
    Month: Optional[int] = None
    DayOfWeek: Optional[str] = None
