"""
Reservoir class for the talkaholic submodule
"""

from typing import Dict, Any
import pandas as pd


class Reservoir:
    """
    A class representing a reservoir dataset that behaves like a pandas DataFrame
    """
    
    def __init__(self, data: Dict[str, Any]):
        """
        Initialize a Reservoir object with the given data
        
        Args:
            data: Dictionary containing reservoir parameters
        """
        self.data = data
        # Create a DataFrame internally for pandas-like behavior
        self._df = pd.DataFrame([data]) if data else pd.DataFrame()
    
    def __repr__(self):
        return f"Reservoir({self.data})"
    
    @property
    def shape(self):
        """Return the shape of the reservoir data (rows, columns)"""
        return self._df.shape
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the reservoir data back to a dictionary"""
        return self.data
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert the reservoir data to a pandas DataFrame"""
        return self._df.copy()
    
    def get_field(self, field_name: str, default: Any = None) -> Any:
        """
        Get any field from the original data with a default value
        
        Args:
            field_name: Name of the field to retrieve
            default: Default value if field doesn't exist
            
        Returns:
            The field value or default
        """
        return self.data.get(field_name, default)