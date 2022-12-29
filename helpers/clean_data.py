from datetime import datetime, date, timedelta


def clean_date(user_date):
    user_date = user_date.lower()

    if user_date == "today":
        user_date = date.today()
    elif user_date == "yesterday":
        user_date = date.today() - timedelta(days=1)
    elif "/" in user_date:
        date_format = '%m/%d/%Y'
        user_date = datetime.strptime(user_date, date_format).date()
    elif "-" in user_date:
        date_format = '%m-%d-%Y'
        user_date = datetime.strptime(user_date, date_format).date()

    return user_date
