from typing import List, Dict, Any

class CarHistorySummary:

    def __init__(self):
        self.data: Dict[ int, Dict[int, Dict[str, Any]]] = {};

    def updateCarHistorySummary(self, driver_id: int, carHistorySummaryList: List[Any]) -> None:

        if carHistorySummaryList is None: 
            self.data[driver_id] = {};
            return
    
        lap_number = carHistorySummaryList[0];

        # Initialize the dict with driver_id if it does not already exist
        if driver_id not in self.data:
            self.data[driver_id] = {};

        self.data[driver_id][lap_number] = {
            'carPosition': carHistorySummaryList[1],
            'tyreRLWear': carHistorySummaryList[2],
            'tyreRRWear': carHistorySummaryList[3],
            'tyreFLWear': carHistorySummaryList[4],
            'tyreFRWear': carHistorySummaryList[5],
            'ersHarvested': carHistorySummaryList[6],
            'isInPits': carHistorySummaryList[7]
        };

    def getCarHistorySummary(self, driver_id: int) -> Dict[int, Dict[str, Any]]:

        return self.data.get(driver_id);