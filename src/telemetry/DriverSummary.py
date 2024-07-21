from typing import List, Dict, Any

class DriverSummary:

    def __init__(self):

        self.data: Dict[int, Dict[int, Dict[str, Any]]] = {};
    
    def updateDriverSummary(self, driver_id: int, summary_list: List[Any]) -> None:

        if summary_list is None: 
            self.data[driver_id] = {};
            return
    
        lap_number = summary_list[0];

        # Initialize the dict with driver_id if it does not already exist
        if driver_id not in self.data:
            self.data[driver_id] = {};
        
        self.data[driver_id][lap_number] = {

            'carPosition': summary_list[1],
            'last_lapTime': summary_list[2],
            'time_sector1': summary_list[3],
            'time_sector2': summary_list[4],
            'time_sector3': summary_list[5]
        }

    def getDriverSummary(self, driver_id: int) -> Dict[int, Dict[str, Any]]:

        return self.data.get(driver_id);
    
