import factory
import datetime
from factory.fuzzy import FuzzyText, FuzzyDate
from django.contrib.auth.models import User
from core.models import Project, Task, Timer

class ProjectFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Project

    name = FuzzyText(length=2, prefix="test_project")
    price_per_hour = 4000

class TaskFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Task

    name = FuzzyText(length=2, prefix="task")
    description = "A test task"
    project = factory.SubFactory(ProjectFactory)
    started = False

class TimerFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Timer

    initial_time = None
    final_time = None
    task = factory.SubFactory(TaskFactory)
