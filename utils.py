"""
Utility functions for the Student Dashboard application.
Handles age calculation, filtering, and data processing.
"""
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any
import pandas as pd


def calculate_age(dob_str: str) -> int:
    """
    Calculate age from date of birth string.
    
    Args:
        dob_str: Date of birth in 'YYYY-MM-DD' format
        
    Returns:
        Age as integer
    """
    try:
        dob = datetime.strptime(dob_str, "%Y-%m-%d")
        today = datetime.today()
        
        age = today.year - dob.year - (
            (today.month, today.day) < (dob.month, dob.day)
        )
        return max(0, age)  # Ensure non-negative
    except (ValueError, TypeError):
        return 0


def add_age_to_students(rows: List[Tuple]) -> List[Tuple]:
    """
    Add calculated age to student records.
    
    Args:
        rows: List of student tuples (no, roll, name, gender, father, dob, class)
        
    Returns:
        List of tuples with age appended
    """
    data_with_age = []
    for row in rows:
        no, roll, name, gender, father, dob, class_name = row
        age = calculate_age(dob)
        data_with_age.append((no, roll, name, gender, father, dob, class_name, age))
    return data_with_age


def apply_filters(
    data: List[Tuple],
    class_filter: str = 'all',
    gender_filter: str = 'all',
    age_single: Optional[int] = None,
    age_min: Optional[int] = None,
    age_max: Optional[int] = None
) -> List[Tuple]:
    """
    Apply multiple filters to student data.
    
    Args:
        data: List of student tuples with age at index 7
        class_filter: Class filter ('all', 's1', 's2', 's3', 's4')
        gender_filter: Gender filter ('all', 'ကျား', 'မ')
        age_single: Single age to filter by
        age_min: Minimum age for range filter
        age_max: Maximum age for range filter
        
    Returns:
        Filtered list of student tuples
    """
    filtered_data = data
    
    # Apply class filter
    if class_filter != 'all':
        filtered_data = [row for row in filtered_data if row[6] == class_filter]
    
    # Apply gender filter
    if gender_filter != 'all':
        filtered_data = [row for row in filtered_data if row[3] == gender_filter]
    
    # Apply single age filter
    if age_single is not None:
        filtered_data = [row for row in filtered_data if row[7] == age_single]
    
    # Apply age range filter
    elif age_min is not None and age_max is not None:
        filtered_data = [
            row for row in filtered_data 
            if age_min <= row[7] <= age_max
        ]
    
    return filtered_data


def calculate_summary(data: List[Tuple]) -> Dict[str, int]:
    """
    Calculate summary statistics from student data.
    
    Args:
        data: List of student tuples with gender at index 3
        
    Returns:
        Dictionary with 'all', 'male', 'female' counts
    """
    return {
        'all': len(data),
        'male': len([r for r in data if r[3] == 'ကျား']),
        'female': len([r for r in data if r[3] == 'မ'])
    }


def read_excel_students(file_path: str) -> List[Dict[str, Any]]:
    """
    Read student data from Excel file.
    
    Args:
        file_path: Path to Excel file
        
    Returns:
        List of dictionaries containing student data
    """
    try:
        df = pd.read_excel(file_path)
        df.columns = df.columns.str.strip()
        
        # Convert birthday to string format
        if 'မွေးနေ့' in df.columns:
            df['မွေးနေ့'] = pd.to_datetime(df['မွေးနေ့']).dt.strftime('%Y-%m-%d')
        
        return df.to_dict('records')
    except Exception as e:
        raise ValueError(f"Error reading Excel file: {e}")


def export_to_excel(data: List[Tuple], output_path: str, include_class: bool = True) -> bool:
    """
    Export student data to Excel file.
    
    Args:
        data: List of student tuples
        output_path: Output file path
        include_class: Whether to include class field
        
    Returns:
        True if successful
    """
    try:
        no = []
        school_no = []
        name = []
        gender = []
        f_name = []
        b_day = []
        age = []
        class_list = []
        
        for row in data:
            no.append(row[0])
            school_no.append(row[1])
            name.append(row[2])
            gender.append(row[3])
            f_name.append(row[4])
            b_day.append(row[5])
            age.append(row[7])
            if include_class:
                class_list.append(row[6])
        
        export_data = {
            'စဉ်': no,
            'ကျောင်းဝင်အမှတ်': school_no,
            'နံမည်': name,
            'ကျားမ': gender,
            'အဖေနံမည်': f_name,
            'မွေးနေ့': b_day,
            'အသက်': age
        }
        
        if include_class:
            export_data['class'] = class_list
        
        df = pd.DataFrame(export_data)
        df.to_excel(output_path, index=False)
        
        return True
    except Exception as e:
        print(f"Export error: {e}")
        return False


def validate_file_path(file_path: str) -> bool:
    """Check if a file exists and is readable."""
    import os
    return os.path.exists(file_path) and os.path.isfile(file_path)


def get_default_context() -> Dict[str, Any]:
    """Get default template context for initial page load."""
    return {
        'data': [],
        'data_all': 0,
        'data_male': 0,
        'data_female': 0,
        'age': '',
        'age_1': '',
        'age_2': '',
        'class_html': 'all',
        'gender': 'all',
        'message': '',
        'message_type': ''
    }