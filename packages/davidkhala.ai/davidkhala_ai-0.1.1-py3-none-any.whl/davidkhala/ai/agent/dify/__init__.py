from datetime import datetime


def with_datetime(filename:str):
    if ' ' in filename:
        raise ValueError(f"Filename '{filename}' should not contain spaces.")
    return f"{datetime.now().strftime("%Y%m%d_%H%M%S")}.{filename}"


