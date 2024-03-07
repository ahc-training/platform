import jenkinsapi
from jenkinsapi.jenkins import Jenkins
jenkins_url = "http://jenkins.example.com"
server = Jenkins(jenkins_url,username="sysadmin",password="vagrant")
print(server.get_job("Spark_container_image_for_Airflow").get_last_buildnumber())