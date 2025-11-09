from dataclasses import dataclass

@dataclass
class GoogleAiResponse:
    guests_qty: int
    beds_qty: int
    pnp_beds_qty: int
    car_make: str
    car_model: str
    car_color: str
    car_license_number: str
    car_license_state: str
