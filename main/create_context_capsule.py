from datetime import datetime

def create_context_capsule(context_id):
    year = datetime.now().year
    month = datetime.now().month
    day = datetime.now().day
    return  {"context_id": context_id,
             "date": date(year, month, day),
             "place": None,
             "place_id": None,
             "country": None,
             "region": None,
             "city": None}