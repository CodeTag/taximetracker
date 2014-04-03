class TimeDelta:
    def __init__(self, _seconds):
        self.seconds = _seconds

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

        if self.seconds == None:
            return "00:00:00"

        hours = self.seconds / 3600
        minutes = (self.seconds % 3600) / 60
        seconds = (self.seconds % 3600) % 60

        return "%.2d:%.2d:%.2d" % (hours, minutes, seconds)
