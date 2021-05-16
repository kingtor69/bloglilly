

def generate_preview(statement, length):
    listed_statement = list(statement)
    if len(list(statement)) < length:
        return statement
    preview = ""
    for i in range(length):
        if i < (length - 3):
            preview += listed_statement[i]
        elif i < (length):
            preview += '.'
    return preview

# def pretify_datetime(date_time):
#     """generate user-readable and pretty-looking date/time from SQL datetime"""

#     # pretify month
#     month_num = date_time.month
#     months = ['no zero month', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
#     month = months[date_time.month]

#     # translate 24-hour time to am/pm
#     ampm = "am"
#     if date_time.hour > 12:
#         hour = date_time.hour - 12
#         ampm = "pm"
#     else: 
#         hour = date_time.hour

#     return f"{date_time.year} {month} {date_time.day} at {hour}:{date_time.minute}{ampm} UTC"