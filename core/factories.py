import factory
from core.models import Project

class ProjectFactory(factory.Factory):
    FACTORY_FOR = Project

    name = "test_project"
    price_per_hour = 4000
