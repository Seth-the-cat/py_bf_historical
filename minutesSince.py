from datetime import datetime
def minutesSince(input):
    input_dt = datetime.strptime(input, "%Y-%m-%dT%H:%M:%S.%f")
    diff = datetime.now() - input_dt
    return int(diff.total_seconds() / 60)

#def test_minutesSince(input):
#    return datetime.fromisoformat(input).strftime("%m/%d/%y %H:%M:%S")
