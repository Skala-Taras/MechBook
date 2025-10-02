"""
Factories for test data.

Ten moduł zawiera klasy i funkcje do generowania danych testowych
dla modeli aplikacji. Używamy prostych fabryk bez dodatkowych bibliotek.
"""
from typing import Dict, Any


class MechanicFactory:
    """Factory for creating mechanic data."""
    
    _counter = 0
    
    @classmethod
    def build(
        cls,
        email: str = None,
        name: str = None,
        password: str = "password123"
    ) -> Dict[str, Any]:
        """
        Creates mechanic data (without saving to database).
        
        Args:
            email: Email (if None, generates unique)
            name: Name (if None, generates)
            password: Password (default 'password123')
        
        Returns:
            Dict with registration data
        """
        cls._counter += 1
        
        if email is None:
            email = f"mechanic{cls._counter}@example.com"
        
        if name is None:
            name = f"Mechanic {cls._counter}"
        
        return {
            "email": email,
            "name": name,
            "password": password
        }
    
    @classmethod
    def build_batch(cls, size: int = 3, **kwargs) -> list[Dict[str, Any]]:
        """
        Creates a list of mechanic data.
        
        Args:
            size: Number of mechanics to create
            **kwargs: Additional arguments passed to build()
        
        Returns:
            List of dictionaries with mechanic data
        """
        return [cls.build(**kwargs) for _ in range(size)]
    
    @classmethod
    def reset_counter(cls):
        """Resets the counter (useful in fixtures)."""
        cls._counter = 0


class ClientFactory:
    """Factory for creating client data."""
    
    _counter = 0
    
    @classmethod
    def build(
        cls,
        first_name: str = None,
        last_name: str = None,
        phone_number: str = None,
        email: str = None
    ) -> Dict[str, Any]:
        """Creates client data."""
        cls._counter += 1
        
        return {
            "first_name": first_name or f"Client{cls._counter}",
            "last_name": last_name or f"Lastname{cls._counter}",
            "phone_number": phone_number or f"12345678{cls._counter:02d}",
            "email": email or f"client{cls._counter}@example.com"
        }
    
    @classmethod
    def build_batch(cls, size: int = 3, **kwargs) -> list[Dict[str, Any]]:
        """Creates a list of client data."""
        return [cls.build(**kwargs) for _ in range(size)]
    
    @classmethod
    def reset_counter(cls):
        """Resets the counter."""
        cls._counter = 0


class VehicleFactory:
    """Factory for creating vehicle data."""
    
    _counter = 0
    
    @classmethod
    def build(
        cls,
        brand: str = None,
        model: str = None,
        vin: str = None,
        production_year: int = 2020,
        engine_capacity: str = "2.0",
        horse_power: str = "150",
        fuel_type: str = "Benzyna"
    ) -> Dict[str, Any]:
        """Creates vehicle data."""
        cls._counter += 1
        
        return {
            "brand": brand or f"Brand{cls._counter}",
            "model": model or f"Model{cls._counter}",
            "vin": vin or f"VIN{cls._counter:013d}",
            "production_year": production_year,
            "engine_capacity": engine_capacity,
            "horse_power": horse_power,
            "fuel_type": fuel_type
        }
    
    @classmethod
    def build_batch(cls, size: int = 3, **kwargs) -> list[Dict[str, Any]]:
        """Creates a list of vehicle data."""
        return [cls.build(**kwargs) for _ in range(size)]
    
    @classmethod
    def reset_counter(cls):
        """Resets the counter."""
        cls._counter = 0


# Fixture to reset factories before each test
def reset_all_factories():
    """Resets all factory counters."""
    MechanicFactory.reset_counter() 
    ClientFactory.reset_counter()
    VehicleFactory.reset_counter()

