from django.test import TestCase, RequestFactory
from core.models import Project, Task, Timer
from django.contrib.auth.models import User
from views import home, projects, yourtasks, fast_task, yourtasks_current_month
from views import create_task, create_project
from core.models import start_task, stop_task
from core.lib.time_delta import TimeDelta
from factories import ProjectFactory, TaskFactory, TimerFactory

from registration.models import RegistrationProfile

from django.test import LiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver

from datetime import timedelta, datetime

class TaskRedirectionTests(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        cls.selenium = WebDriver()
        super(TaskRedirectionTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(TaskRedirectionTests, cls).tearDownClass()

    def test_when_create_task_on_current_month_tasks_its_redirect_to_current_month_tasks(self):

        User.objects.create_user(username="jefree", password="1234")

        self.selenium.get('%s%s' % (self.live_server_url, '/accounts/login/'))

        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('jefree')

        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('1234')

        self.selenium.find_element_by_xpath('//input[@value="Log in"]').click()

        self.selenium.get('%s%s' % (self.live_server_url, '/yourtasks/current_month'))

        #press fasttask button
        self.selenium.find_element_by_xpath('//form[@action="/fasttask/"]').submit()

        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, '/yourtasks/current_month/'))


    def test_when_create_task_on_yourtasks_its_redirect_to_yourtasks(self):

        User.objects.create_user(username="jefree", password="1234")

        self.selenium.get('%s%s' % (self.live_server_url, '/accounts/login/'))

        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('jefree')

        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('1234')

        self.selenium.find_element_by_xpath('//input[@value="Log in"]').click()

        self.selenium.get('%s%s' % (self.live_server_url, '/yourtasks/'))

        #press fasttask button
        self.selenium.find_element_by_xpath('//form[@action="/fasttask/"]').submit()

        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, '/yourtasks/'))


class UserValidationTests(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        cls.selenium = WebDriver()
        super(UserValidationTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(UserValidationTests, cls).tearDownClass()

    def test_user_with_valid_credentials_should_be_able_to_login(self):
        User.objects.create_user(username="cesar", password="1234")

        self.selenium.get('%s%s' % (self.live_server_url, '/accounts/login/'))

        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('cesar')

        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('1234')

        self.selenium.find_element_by_xpath('//input[@value="Log in"]').click()

        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, '/'))

    def test_when_an_anonymous_user_visits_yourtasks_he_should_be_redirected_to_login_page(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/yourtasks/'))
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, '/accounts/login/'))

    def test_when_a_user_with_inactive_account_login_the_body_show_correctly_a_error_message(self):

        RegistrationProfile.objects.create_inactive_user("jefree", "jgarzon920429@gmail.com", "1234", "", False)

        self.selenium.get('%s%s' % (self.live_server_url, '/accounts/login/'))

        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('jefree')

        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('1234')

        self.selenium.find_element_by_xpath('//input[@value="Log in"]').click()

        body = self.selenium.find_element_by_tag_name('body')

        self.assertIn("This account is inactive", body.text)

        self.assertNotIn("__all__", body.text)

    def test_when_a_login_error_ocurrs_the_body_show_correctly_a_error_message(self):
        User.objects.create_user(username="cesar", password="1234")

        self.selenium.get('%s%s' % (self.live_server_url, '/accounts/login/'))

        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('jefree')

        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('miclave123')

        self.selenium.find_element_by_xpath('//input[@value="Log in"]').click()

        body = self.selenium.find_element_by_tag_name('body')

        self.assertIn("Please enter a correct username and password. Note that both fields may be case-sensitive.", body.text)

        self.assertNotIn("__all__", body.text)

class YourTaskTemplateTest(TestCase):

    def test_al_hacer_get_en_yourtask_se_obtienen_dos_enlaces_de_tareas_actuales_y_antiguas(self):
        user = User.objects.create(username="cesar", password="1234")

        factory = RequestFactory()
        request = factory.get("/yourtasks")
        request.user = user
        result = yourtasks(request)

        self.assertIn('<a href="/yourtasks/current_month">Current month</a>',result.content)
        self.assertIn('<a href="/yourtasks/all_tasks">All Tasks</a>',result.content)
        self.assertEqual(result.status_code,200)

    def test_al_hacer_get_en_enlace_de_tareas_del_mes_actual_muestra_solo_esas_tareas(self):
        user = User.objects.create(username="cesar", password="1234")

        t1 = TaskFactory(user=user)
        t1.start()
        t1.stop()

        other_month = datetime.now() - timedelta(days=32)

        t2 = TaskFactory(user=user)
        t2.current_timer = TimerFactory(task=t2, initial_time=other_month)
        t2.stop()

        t3 = TaskFactory(user=user)
        t3.current_timer = TimerFactory(task=t3, initial_time=other_month, final_time=other_month)

        factory = RequestFactory()
        request = factory.get("/yourtasks/current_month")
        request.user = user
        result = yourtasks_current_month(request)
        self.assertIn(t1.name,result.content)
        self.assertIn(t2.name,result.content)
        self.assertNotIn(t3.name,result.content)
        self.assertEqual(result.status_code,200)

    def test_al_hacer_get_en_enlace_de_todas_las_tareas_muestra_esas_tareas(self):

        user = User.objects.create(username="cesar", password="1234")

        project = ProjectFactory()

        t1 = TaskFactory(user=user, project=project)
        t1.start()
        t1.stop()

        other_month = datetime.now() - timedelta(days=32)

        t2 = TaskFactory(user=user,project=project)
        t2.current_timer = TimerFactory(task=t2, initial_time=other_month)
        t2.stop()

        t3 = TaskFactory(user=user,project=project)
        t3.current_timer = TimerFactory(task=t3, initial_time=other_month, final_time=other_month)

        factory = RequestFactory()
        request = factory.get("/yourtasks/")
        request.user = user
        result = yourtasks(request)
        self.assertIn(t1.name,result.content)
        self.assertIn(t2.name,result.content)
        self.assertIn(t3.name,result.content)
        self.assertEqual(result.status_code,200)

class TimeDeltaTest(TestCase):
    def test_seconds_deberia_retornar_86400_cuando_se_pasan_86400_segundos_al_constructor(self):
        delta = TimeDelta(86400)
        self.assertEqual(delta.seconds, 86400)

    def test_minutes_deberia_retornar_1400_cuando_se_pasan_86400_segundos_al_constructor(self):
        delta = TimeDelta(86400)
        self.assertEqual(delta.minutes, 1440)

    def test_hours_deberia_retornar_24_cuando_se_pasan_86400_segundos_al_constructor(self):
        delta = TimeDelta(86400)
        self.assertEqual(delta.hours, 24)

    def test_days_deberia_retornar_1_cuando_se_pasan_86400_segundos_al_constructor(self):
        delta = TimeDelta(86400)
        self.assertEqual(delta.days, 1)

    def test_hours_formated_should_return_00_00_31_when_31_seconds_are_passed_to_the_connstructor(self):
        delta = TimeDelta(31)
        self.assertEqual(delta.hours_formated, "00:00:31")

    def test_hours_formated_should_return_00_15_12_when_912_seconds_are_passed_to_the_connstructor(self):
        delta = TimeDelta(912)
        self.assertEqual(delta.hours_formated, "00:15:12")

    def test_hours_formated_should_return_90_15_12_when_324912_seconds_are_passed_to_the_connstructor(self):
        delta = TimeDelta(324912)
        self.assertEqual(delta.hours_formated, "90:15:12")

    def test_hours_formated_should_return_190_15_12_when_684912_seconds_are_passed_to_the_connstructor(self):
        delta = TimeDelta(684912)
        self.assertEqual(delta.hours_formated, "190:15:12")

    def test_hours_formated_should_return_00_00_00_when_0_seconds_are_passed_to_the_connstructor(self):
        delta = TimeDelta(0)
        self.assertEqual(delta.hours_formated, "00:00:00")

    def test_hours_formated_should_return_00_00_00_when_None_is_passed_to_the_connstructor(self):
        delta = TimeDelta(None)
        self.assertEqual(delta.hours_formated, "00:00:00")

class StartTaskTest(TestCase):

    def test_iniciar_tarea_para_cambiarle_el_estado_y_asignarle_un_timer(self):

        user = User.objects.create(username="cesar", password="1234")
        
        t = TaskFactory(user=user)
        
        start_task(t)
        tasks_started = Task.objects.filter(started=True).count()
        self.assertEqual(tasks_started,1)
        temporal_timer = t.current_timer
        self.assertEqual(temporal_timer, Timer.objects.all()[0])
        timers = Timer.objects.all().count()
        self.assertEqual(timers,1)

class StopTaskTest(TestCase):
    def test_detener_tarea_para_cambiarle_el_estado_y_liberar_su_timer_temporal(self):
        user = User.objects.create(username="cesar", password="1234")
        
        t = TaskFactory(user=user)
        
        start_task(t)
        stop_task(t)
        tasks_stopped = Task.objects.filter(started=False).count()
        self.assertEqual(tasks_stopped,1)
        temporal_timer = t.current_timer
        self.assertEqual(temporal_timer, None)
        timers = Timer.objects.all().count()
        self.assertEqual(timers,1)

class ProjectTest(TestCase):

    def test_al_hacer_post_se_crea_un_proyecto(self):
        user = User.objects.create(username="cesar", password="1234")
        
        factory = RequestFactory()
        request = factory.post("/projects")
        request.POST["projectname"] = "project1"
        request.POST["projectcost"] = 2000
        request.user = user
        
        projects(request)
        projects_number = Project.objects.all().count()
   
        self.assertEqual(projects_number, 1)

class HomeTest(TestCase):

    def test_al_hacer_post_se_crea_una_tarea(self):
        user = User.objects.create(username="cesar", password="1234")

        p = ProjectFactory()

        factory = RequestFactory()
        request = factory.post("/home")
        request.user = user
        request.POST["projectname"] = p.name
        request.POST["taskname"] = "testTask"
        
        home(request)
        
        projects_number = Project.objects.all().count()
        tasks_number = Task.objects.all().count()
        
        self.assertEqual(projects_number, 1)
        self.assertEqual(tasks_number, 1)

class YourtasksTest(TestCase):

    def test_al_hacer_post_para_inciar_una_tarea(self):
        user= User.objects.create(username="cesar",password="1234")
        factory = RequestFactory()
        request = factory.post("/yourtasks")
        
        t = TaskFactory(user=user, started=True)
        
        request.user = user
        request.POST["task_selected"] = t.id
        request.POST["choisebuttom"] = "Start"
        yourtasks(request)
        tasks_started = Task.objects.filter(started=True).count()
        self.assertEqual(tasks_started,1)

    def test_al_hacer_post_para_detener_una_tarea(self):
        user= User.objects.create(username="cesar",password="1234")
        factory = RequestFactory()
        request = factory.post("/yourtasks")
        
        t = TaskFactory(user=user, started=True)
        t.start()

        request.user = user
        request.POST["task_selected"] = t.id
        request.POST["choisebuttom"] = "Stop"
        yourtasks(request)
        tasks_stopped = Task.objects.filter(started=False).count()
        self.assertEqual(tasks_stopped,1)

class FastTaskTest(TestCase):

    def test_al_iniciar_tarea_para_iniciar_una_tarea(self):
        user= User.objects.create(username="cesar",password="1234")
        factory = RequestFactory()
        request = factory.post("/fasttask")
        request.POST["choisebuttom"] = "Start"
        request.user = user
        fast_task(request)
        tasks_started = Task.objects.filter(started=True).count()
        self.assertEqual(tasks_started,1)

    def test_al_detener_tarea_con_ningun_campo_vacio_para_detener_tarea_y_crear_proyecto(self):
        user= User.objects.create(username="cesar",password="1234")
        
        tk = TaskFactory(user=user, name='in_progress', started=True, project=None)
        tk.start()

        factory = RequestFactory()

        request = factory.post("/fasttask")
        request.user = user
        request.POST["taskName"] = "TestTask"
        request.POST["newProjectName"] = "Project1"
        request.POST["choisebuttom"] = "Stop"

        fast_task(request)

        tasks_stopped = Task.objects.filter(started=False).count()
        projects_number = Project.objects.all().count()
        self.assertEqual(tasks_stopped+projects_number,2)

    def test_al_detener_tarea_con_campo_de_tarea_vacio_para_no_detener_tarea_ni_crear_proyecto(self):
        user = User.objects.create(username="cesar",password="1234")

        tk = Task(user=user, name='in_progress', started=True, project=None)
        tk.start()

        factory = RequestFactory()

        request = factory.post("/fasttask")
        request.user = user
        request.POST["taskName"] = ""
        request.POST["newProjectName"] = "Project1"
        request.POST["choisebuttom"] = "Stop"

        fast_task(request)

        tasks_stopped = Task.objects.filter(started=False).count()
        projects_number = Project.objects.all().count()
        self.assertEqual(tasks_stopped+projects_number,0)

    def test_al_detener_tarea_con_campo_de_proyecto_vacio_para_no_detener_tarea_ni_crear_proyecto(self):
        user = User.objects.create(username="cesar",password="1234")
        
        tk = TaskFactory(user=user, name='in_progress', started=True, project=None)
        tk.start()

        factory = RequestFactory()

        request = factory.post("/fasttask")
        request.user = user
        request.POST["taskName"] = "TestTask"
        request.POST["newProjectName"] = ""
        request.POST["choisebuttom"] = "Stop"

        fast_task(request)

        tasks_stopped = Task.objects.filter(started=False).count()
        projects_number = Project.objects.all().count()
        self.assertEqual(tasks_stopped+projects_number,0)

class TaskTest(TestCase):

    def test_iniciar_una_tarea_para_crearle_un_cronometro_temporal_y_darle_su_tiempo_de_inicio(self):
        user = User.objects.create(username="cesar",password="1234")
        
        t1 = TaskFactory(user=user)
        t1.current_timer = TimerFactory(task=t1, initial_time=datetime(2013, 10, 31, 17, 56, 1, 0))

        timers = t1.timer_set.all().count()
        time = t1.current_timer

        self.assertEqual(timers, 1)
        self.assertEqual(time.initial_time.second, 1)

    def test_pausar_una_tarea_para_desvicularle_el_cronometro_temporal_y_asignarle_tiempo_final(self):
        user = User.objects.create(username="cesar",password="1234")

        t1 = TaskFactory(user=user)
        t1.current_timer = TimerFactory(task=t1, final_time=datetime(2013, 10, 31, 17, 56, 1, 0))
        
        time = t1.current_timer
        self.assertEqual(time.final_time.second, 1)
        
        t1.current_timer = None
        t1.save()

        timer_in_task = t1.current_timer
        self.assertEqual(timer_in_task, None)
        
        timers= t1.timer_set.all().count()
        self.assertEqual(timers,1)

    def test_calcular_tiempo_para_devolver_el_tiempo_total_de_una_tarea(self):
        user = User.objects.create(username="cesar",password="1234")

        t1 = TaskFactory(name="Task1",user=user)

        t1.current_timer = TimerFactory(task=t1, initial_time=datetime(2013, 10, 31, 17, 56, 1, 0),
                final_time=datetime(2013, 10, 31, 18, 56, 1, 0))
        
        t1.current_timer = TimerFactory(task=t1, initial_time=datetime(2013, 10, 31, 18, 56, 1, 0),
                final_time=datetime(2013, 10, 31, 19, 56, 1, 0))

        result = t1.calculate_time()
        self.assertEqual(result.hours, 2)

    def test_calcular_costo_para_obtener_el_valor_total_por_una_tarea_con_todos_sus_tiempos(self):
        user = User.objects.create(username="cesar",password="1234")
        
        t1 = TaskFactory(user=user)

        t1.current_timer = TimerFactory(task=t1, initial_time=datetime(2013, 10, 31, 17, 56, 1, 0),
                final_time=datetime(2013, 10, 31, 18, 56, 1, 0))
       
        t1.current_timer = TimerFactory(task=t1, initial_time=datetime(2013, 10, 31, 18, 56, 1, 0),
                final_time=datetime(2013, 10, 31, 19, 56, 1, 0))
        
        result = t1.calculate_cost()
        self.assertEqual(result,8000)

    def test_current_month_tasks_deberia_retortar_solo_las_tareas_que_tienen_timers_en_el_mes_actual(self):
        user = User.objects.create(username="cesar",password="1234")

        last_month = datetime.today() - timedelta(days=32)

        t1 = TaskFactory(user=user)
        t1.current_timer = TimerFactory(task=t1, initial_time=last_month, final_time=last_month)

        t2 = TaskFactory(user=user)
        t2.current_timer = TimerFactory(task=t2, initial_time=last_month, final_time=datetime.today())

        t3 = TaskFactory(user=user)
        t3.current_timer = TimerFactory(task=t3, initial_time=datetime.today(), final_time=datetime.today())

        result = Task.objects.current_month_tasks()
        
        self.assertEqual(set(result), set([t2, t3]))

    def test_create_task_debe_crear_una_tarea_con_todos_sus_elementos_a_partir_de_datos_validos(self):
        user = User.objects.create(username="cesar",password="1234")
        
        project = ProjectFactory()
        
        factory = RequestFactory()
        request = factory.post("/yourtasks")
        request.user = user
        request.POST["taskname"] = "TestTask"
        request.POST["taskdescription"] = "TestDescription"
        create_task(request, project)

    def test_create_project_debe_crear_un_proyecto_con_todos_sus_elementos_a_partir_de_datos_validos(self):
        factory = RequestFactory()
        
        request = factory.post("/yourtasks")
        request.POST["projectname"] = "TestProject"
        request.POST["projectcost"] = 8000
        
        create_project(request)
        projects = Project.objects.all().count()
        
        self.assertEqual(projects, 1)

    def test_create_task_no_debe_crear_tarea_si_no_hay_un_usuario_predefinido(self):
        project = ProjectFactory()
        
        factory = RequestFactory()
        request = factory.post("/yourtasks")
        request.POST["taskname"] = ""
        request.POST["taskdescription"] = "TestTask"
        self.assertRaises(AttributeError,create_task, request, project)
        tasks = Task.objects.all().count()
        self.assertEqual(tasks, 0)

    def test_create_task_debe_crear_una_tarea_aunque_esten_todos_sus_campos_vacios_menos_el_usuario(self):
        user = User.objects.create(username="cesar",password="1234")

        project = ProjectFactory()
        
        factory = RequestFactory()
        request = factory.post("/yourtasks")
        request.user = user
        create_task(request, project)
        tasks = Task.objects.all().count()
        self.assertEqual(tasks, 1)

    def test_create_project_no_debe_crear_un_proyecto_si_no_se_ingresa_un_precio_valido_del_mismo(self):
        factory = RequestFactory()
        request = factory.post("/yourtasks")
        request.POST["projectname"] = "TestProject"
        request.POST["projectcost"] = ""
        self.assertRaises(ValueError,create_project, request)
        projects = Project.objects.all().count()
        self.assertEqual(projects, 0)
