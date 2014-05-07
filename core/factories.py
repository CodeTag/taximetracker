import factory
from factory.fuzzy import FuzzyText
from django.contrib.auth.models import User
from core.models import Project, Task

class ProjectFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Project

    name = "test_project"
    price_per_hour = 4000

class TaskFactory(factory.DjangoModelFactory):
	FACTORY_FOR = Task

	name = FuzzyText(length=2, prefix="task")
	description = "A test task"
	project = factory.SubFactory(ProjectFactory)
	started = False

