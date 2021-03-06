class TimeDelta:
    def __init__(self, _seconds):
        self.seconds = _seconds or 0

    @property
    def minutes(self):
        return self.seconds / 60.0

    @property
    def hours(self):
        return self.minutes / 60.0

    @property
    def days(self):
        return self.hours / 24.0

    @property
    def hours_formated(self):

        hours = self.hours

        remaining_seconds = self.seconds % 3600

        minutes = (remaining_seconds) / 60
        seconds = (remaining_seconds) % 60

        return "%.2d:%.2d:%.2d" % (hours, minutes, seconds)
