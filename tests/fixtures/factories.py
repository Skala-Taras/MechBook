"""
Fabryki danych testowych.

Ten moduł zawiera klasy i funkcje do generowania danych testowych
dla modeli aplikacji. Używamy prostych fabryk bez dodatkowych bibliotek.
"""
from typing import Dict, Any


class MechanicFactory:
    """Fabryka do tworzenia danych mechaników."""
    
    _counter = 0
    
    @classmethod
    def build(
        cls,
        email: str = None,
        name: str = None,
        password: str = "password123"
    ) -> Dict[str, Any]:
        """
        Tworzy dane mechanika (bez zapisu do bazy).
        
        Args:
            email: Email (jeśli None, generuje unikalny)
            name: Imię (jeśli None, generuje)
            password: Hasło (domyślnie 'password123')
        
        Returns:
            Dict z danymi do rejestracji
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
        Tworzy listę danych mechaników.
        
        Args:
            size: Liczba mechaników do utworzenia
            **kwargs: Dodatkowe argumenty przekazywane do build()
        
        Returns:
            Lista słowników z danymi mechaników
        """
        return [cls.build(**kwargs) for _ in range(size)]
    
    @classmethod
    def reset_counter(cls):
        """Resetuje licznik (przydatne w fixture'ach)."""
        cls._counter = 0


class ClientFactory:
    """Fabryka do tworzenia danych klientów."""
    
    _counter = 0
    
    @classmethod
    def build(
        cls,
        first_name: str = None,
        last_name: str = None,
        phone_number: str = None,
        email: str = None
    ) -> Dict[str, Any]:
        """Tworzy dane klienta."""
        cls._counter += 1
        
        return {
            "first_name": first_name or f"Client{cls._counter}",
            "last_name": last_name or f"Lastname{cls._counter}",
            "phone_number": phone_number or f"12345678{cls._counter:02d}",
            "email": email or f"client{cls._counter}@example.com"
        }
    
    @classmethod
    def build_batch(cls, size: int = 3, **kwargs) -> list[Dict[str, Any]]:
        """Tworzy listę danych klientów."""
        return [cls.build(**kwargs) for _ in range(size)]
    
    @classmethod
    def reset_counter(cls):
        """Resetuje licznik."""
        cls._counter = 0


class VehicleFactory:
    """Fabryka do tworzenia danych pojazdów."""
    
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
        """Tworzy dane pojazdu."""
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
        """Tworzy listę danych pojazdów."""
        return [cls.build(**kwargs) for _ in range(size)]
    
    @classmethod
    def reset_counter(cls):
        """Resetuje licznik."""
        cls._counter = 0


# Fixture do resetowania fabryk przed każdym testem
def reset_all_factories():
    """Resetuje wszystkie liczniki fabryk."""
    MechanicFactory.reset_counter()
    ClientFactory.reset_counter()
    VehicleFactory.reset_counter()

