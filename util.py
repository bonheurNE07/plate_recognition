import string
import easyocr

# Initialize the OCR reader
reader = easyocr.Reader(['en'], gpu=False)

# Comprehensive mapping dictionaries for character-to-digit and digit-to-character conversion
dict_char_to_int = {'O': '0', 'I': '1', 'J': '3', 'A': '4', 'G': '6', 'S': '5', 'B': '8', 'Z': '2'}
dict_int_to_char = {'0': 'C', '1': 'I', '3': 'J', '4': 'A', '6': 'G', '5': 'S', '8': 'B', '2': 'Z'}

def license_complies_format(text):
    """
    Check if the license plate text complies with the Rwandan format.

    Args:
        text (str): License plate text.

    Returns:
        bool: True if the license plate complies with the format, False otherwise.
    """
    if len(text) == 7:  # Format: RAB123C
        return (text[0] == 'R' and
                text[1] in string.ascii_uppercase and
                text[2] in string.ascii_uppercase and
                text[3] in string.digits and
                text[4] in string.digits and
                text[5] in string.digits and
                text[6] in string.ascii_uppercase)
    elif len(text) == 8:  # Format: RAB123CD
        return (text[0] == 'R' and
                text[1] in string.ascii_uppercase and
                text[2] in string.ascii_uppercase and
                text[3] in string.digits and
                text[4] in string.digits and
                text[5] in string.digits and
                text[6] in string.ascii_uppercase and
                text[7] in string.ascii_uppercase)
    else:
        return False

def format_license(text):
    """
    Format the license plate text by converting characters using the mapping dictionaries
    and ensuring it follows the Rwandan license plate format.

    Args:
        text (str): License plate text.

    Returns:
        str: Formatted license plate text.
    """
    license_plate_ = 'R'  # Force the first character to be 'R'
    
    # Ensure the second and third characters are letters
    for j in range(1, 3):
        if text[j] in dict_int_to_char:  # If a digit looks like a letter, convert it back
            license_plate_ += dict_int_to_char[text[j]]
        elif text[j] in string.ascii_uppercase:
            license_plate_ += text[j]
        else:
            license_plate_ += 'A'  # Default to 'A' if an error occurs

    # Ensure the next three characters are digits
    for j in range(3, 6):
        if text[j] in dict_char_to_int:  # If a letter looks like a digit, convert it back
            license_plate_ += dict_char_to_int[text[j]]
        elif text[j] in string.digits:
            license_plate_ += text[j]
        else:
            license_plate_ += '0'  # Default to '0' if an error occurs

    # Ensure the last character is a letter
    if len(text) > 6:
        if text[6] == 'O':
            license_plate_ += 'C'
        elif text[6] in dict_int_to_char:  # If a digit looks like a letter, convert it back
            license_plate_ += dict_int_to_char[text[6]]
        elif text[6] in string.ascii_uppercase:
            license_plate_ += text[6]
        else:
            license_plate_ += 'A'  # Default to 'A' if an error occurs

    return license_plate_
    
def read_license_plate(license_plate_crop):
    """
    Read the license plate text from the given cropped image.

    Args:
        license_plate_crop (PIL.Image.Image): Cropped image containing the license plate.

    Returns:
        tuple: Tuple containing the corrected license plate text and its confidence score.
    """
    detections = reader.readtext(license_plate_crop)

    for detection in detections:
        bbox, text, score = detection
        text = text.upper().replace(' ', '')  # Remove spaces and convert to uppercase
        
        if len(text) >= 7:
            formatted_license = format_license(text)
            
            if license_complies_format(formatted_license):
                return formatted_license, score
    
    return None, None
