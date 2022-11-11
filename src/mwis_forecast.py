from typing import Dict


class MwisForecast():
    """TODO: storing all data as class attributes is odd. I just had to check, but if you modify
    instance.class_variable then the value only changes for that particular instance (as long as
    the variable is an immutable type).
    """
    location: str = ""
    date: str = ""
    days_ahead: int = 0
    headline: str = ""
    how_wet: str = ""
    how_windy: str = ""
    cloud_on_hills: str = ""
    chance_cloud_free: str = ""
    sunshine: str = ""
    how_cold: str = ""
    freezing_level: str = ""

    def __iter__(self):
        """Sorted iteration over attribute names
        """
        for k in sorted(self.__annotations__):
            yield k

    def __repr__(self) -> str:
        return f"MwisForecast(location={self.location}, date={self.date}, days_ahead={self.days_ahead})"

    def __len__(self) -> int:
        return 11

    @staticmethod
    def attr_to_section_title() -> Dict:
        """Mapping from attribute name to section title in HTML
        """
        return {"how_wet": "How Wet?",
                 "how_windy": "How windy? (On the Munros)",
                 "cloud_on_hills": "Cloud on the hills?",
                 "chance_cloud_free": "Chance of cloud free Munros?",
                 "sunshine": "Sunshine and air clarity?",
                 "how_cold": "How Cold? (at 900m)",
                 "freezing_level": "Freezing Level"}
            

