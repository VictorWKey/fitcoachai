"""
Utility functions for handling different load types and conversions.
"""

from typing import Optional, Dict, Union, Tuple
from db.models.programmed_exercise import LoadType

def calculate_weight_from_load(
    load_type: LoadType, 
    load_value: str, 
    one_rm: Optional[float] = None, 
    rpe_table: Optional[Dict[Tuple[int, float], float]] = None
) -> Optional[float]:
    """
    Calculate the actual weight to be used based on the load type and user's one-rep max.
    
    Args:
        load_type: Type of load (RPE, percentage, weight)
        load_value: Value of the load (e.g., "8" for RPE, "75%" for percentage)
        one_rm: User's one-rep max for the exercise, required for percentage calculations
        rpe_table: RPE conversion table, required for RPE calculations
        
    Returns:
        Calculated weight in kg or None if calculation is not possible
    """
    if load_type == LoadType.WEIGHT:
        try:
            # If load_value is just a number like "100"
            return float(load_value)
        except ValueError:
            # If load_value is a range like "100-110", take the average
            if "-" in load_value:
                try:
                    low, high = map(float, load_value.split("-"))
                    return (low + high) / 2
                except (ValueError, AttributeError):
                    return None
            return None
            
    elif load_type == LoadType.PERCENTAGE:
        if one_rm is None:
            return None
            
        try:
            # Remove any % sign and convert to float
            percentage = float(load_value.replace("%", ""))
            return one_rm * percentage / 100
        except (ValueError, AttributeError):
            return None
            
    elif load_type == LoadType.RPE:
        if one_rm is None or rpe_table is None:
            return None
            
        try:
            # Extract RPE value (e.g., "8" from "8 RPE")
            rpe_value = float(load_value.replace("RPE", "").strip())
            
            # Find the closest RPE-reps match in the table
            # This is simplified and would need a real RPE table implementation
            # Example: rpe_table[(8, 5)] = 0.81 means 81% of 1RM for 8 RPE at 5 reps
            # Returns percentage of 1RM
            # This is placeholder logic - you would need a proper RPE table
            
            return None  # Need proper RPE implementation with reps
        except (ValueError, AttributeError):
            return None
    
    return None

def estimate_rpe_from_weight(
    weight: float,
    reps: int,
    one_rm: float,
    rpe_table: Dict[Tuple[int, float], float]
) -> Optional[float]:
    """
    Estimate the RPE based on weight, reps, and one-rep max.
    
    Args:
        weight: Weight used in kg
        reps: Number of repetitions
        one_rm: User's one-rep max for the exercise
        rpe_table: RPE conversion table
        
    Returns:
        Estimated RPE value or None if estimation is not possible
    """
    # Simplified placeholder for RPE estimation
    # In a real implementation, you would use the RPE table and interpolation
    if one_rm <= 0:
        return None
        
    percentage_of_1rm = weight / one_rm * 100
    
    # This would need proper RPE lookup logic
    # Placeholder return
    return None  # Need proper RPE implementation
