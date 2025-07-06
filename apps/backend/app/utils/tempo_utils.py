"""
Utilities for working with exercise tempo formats.

This module provides functions to parse, validate, and format exercise tempo strings.
Tempo is represented as a string in the format "E-B-C-T" where:
- E = Eccentric phase (lowering) in seconds
- B = Bottom position pause in seconds
- C = Concentric phase (lifting) in seconds
- T = Top position pause in seconds

Examples:
- "3-1-1-0": 3 seconds down, 1 second pause at bottom, 1 second up, no pause at top
- "2-0-X-0": 2 seconds down, no pause, explosive up (X), no pause at top
- "4-2-1-1": 4 seconds down, 2 seconds pause, 1 second up, 1 second pause at top
"""

from typing import Tuple, Optional, List, Union, Dict
import re

# Regular expression for validating tempo format
TEMPO_REGEX = re.compile(r'^(\d+|X)-(\d+|X)-(\d+|X)-(\d+|X)$')
TEMPO_REGEX_3_PART = re.compile(r'^(\d+|X)-(\d+|X)-(\d+|X)$')


def validate_tempo(tempo: str) -> bool:
    """
    Validate if a tempo string is in the correct format.
    
    Args:
        tempo: Tempo string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not tempo:
        return False
        
    # Check if it's a 4-part tempo
    if TEMPO_REGEX.match(tempo):
        return True
        
    # Check if it's a 3-part tempo
    if TEMPO_REGEX_3_PART.match(tempo):
        return True
        
    return False


def parse_tempo(tempo: str) -> Dict[str, Union[int, str]]:
    """
    Parse a tempo string into a dictionary of phase durations.
    
    Args:
        tempo: Tempo string in format "E-B-C-T" or "E-B-C"
        
    Returns:
        Dict with keys 'eccentric', 'bottom', 'concentric', 'top'
        
    Raises:
        ValueError: If the tempo string is invalid
    """
    if not validate_tempo(tempo):
        raise ValueError(f"Invalid tempo format: {tempo}. Expected format: 'E-B-C-T' or 'E-B-C'")
    
    parts = tempo.split('-')
    
    result = {
        'eccentric': parts[0],
        'bottom': parts[1],
        'concentric': parts[2],
        'top': '0'  # Default for 3-part tempo
    }
    
    # Add top pause if it's a 4-part tempo
    if len(parts) == 4:
        result['top'] = parts[3]
    
    # Convert numeric values to integers
    result_with_types: Dict[str, Union[int, str]] = {}
    for key, value in result.items():
        if value != 'X':
            result_with_types[key] = int(value)
        else:
            result_with_types[key] = value
    
    return result_with_types


def format_tempo(
    eccentric: Union[int, str],
    bottom: Union[int, str],
    concentric: Union[int, str],
    top: Union[int, str] = 0
) -> str:
    """
    Format tempo components into a tempo string.
    
    Args:
        eccentric: Duration of eccentric phase (or 'X' for explosive)
        bottom: Duration of pause at bottom (or 'X' for no pause)
        concentric: Duration of concentric phase (or 'X' for explosive)
        top: Duration of pause at top (or 'X' for no pause)
        
    Returns:
        str: Formatted tempo string
    """
    return f"{eccentric}-{bottom}-{concentric}-{top}"


def tempo_to_display(tempo: str) -> str:
    """
    Convert a tempo string to a human-readable description.
    
    Args:
        tempo: Tempo string in format "E-B-C-T" or "E-B-C"
        
    Returns:
        str: Human-readable description
    """
    if not tempo or not validate_tempo(tempo):
        return "Tempo no especificado"
    
    parts = parse_tempo(tempo)
    
    descriptions = []
    
    # Eccentric phase
    if parts['eccentric'] == 'X':
        descriptions.append("bajada explosiva")
    else:
        descriptions.append(f"{parts['eccentric']}s bajada")
    
    # Bottom pause
    if parts['bottom'] == 'X':
        descriptions.append("sin pausa abajo")
    elif parts['bottom'] != 0:
        descriptions.append(f"{parts['bottom']}s pausa abajo")
    
    # Concentric phase
    if parts['concentric'] == 'X':
        descriptions.append("subida explosiva")
    else:
        descriptions.append(f"{parts['concentric']}s subida")
    
    # Top pause
    if parts['top'] == 'X':
        descriptions.append("sin pausa arriba")
    elif parts['top'] != 0:
        descriptions.append(f"{parts['top']}s pausa arriba")
    
    return ", ".join(descriptions) 

def fix_tempo_format(tempo: str) -> str:
    """
    Try to fix common formatting issues in a tempo string.
    
    Args:
        tempo: Tempo string to fix
        
    Returns:
        str: Fixed tempo string
    """
    try:
      # Remove spaces
      tempo = tempo.replace(" ", "")
      
      # Handle comma-separated format
      if "," in tempo:
          tempo = tempo.replace(",", "-")
          
      # Handle other common separators
      for sep in ["/", ":", "."]:
          if sep in tempo:
              tempo = tempo.replace(sep, "-")
              
      # Convert to uppercase if 'x' is used instead of 'X'
      if "x" in tempo:
          tempo = tempo.replace("x", "X")
          
      # If still invalid after fixes, use default
      if not validate_tempo(tempo):
          # Default: moderate tempo (2-0-2-0)
          tempo = "2-0-2-0"
          print(f"Warning: Invalid tempo format provided. Using default: {tempo}")
      elif len(tempo.split('-')) == 3:
          # If 3-part tempo is provided, convert to 4-part by adding 0 for top pause
          tempo = f"{tempo}-0"
    except Exception as e:
        # Fallback to default if any error occurs
        tempo = "2-0-2-0"
        print(f"Error processing tempo: {e}. Using default: {tempo}")

    return tempo