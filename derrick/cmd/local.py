from derrick.conf.application_conf import ApplicationConf
from derrick.conf.derrick_conf import DERRICK_BASE_PATH
import os
import inquirer
import chalk as log
import time


def install(platform_git_repo):
    if os.path.exists(DERRICK_BASE_PATH) == False:
        os.system("mkdir -p %s" % DERRICK_BASE_PATH)

    buildpacks_path = os.path.join(DERRICK_BASE_PATH, "buildpacks")

    if os.path.exists(buildpacks_path) == False:
        os.system("mkdir -p %s" % buildpacks_path)

    try:
        os.chdir(buildpacks_path)
        os.system("git clone %s" % (platform_git_repo))
    except Exception, e:
        log.red("Failed to install the specific platform buildpack")
        exit(-1)


def test():
    cwd = os.getcwd()
    test_image_path = os.path.join(cwd, "Dockerfile.test")
    if os.path.exists(test_image_path) == False:
        log.red("Failed to find Dockerfile.test in path")
        exit(-1)

    application_conf = ApplicationConf.parse_application_conf()

    if application_conf == None or application_conf.get("test_image_name") == None:
        ApplicationConf.update_application_conf({
            "test_image_name": (os.path.basename(os.getcwd()) + "-" + str(time.time()) + ":test").lower(),
        })

    application_conf = ApplicationConf.parse_application_conf()
    test_image_repo = application_conf.get("test_image_name")

    cwd = os.getcwd()

    try:
        os.system("docker build -t %s -f %s %s" % (test_image_repo, test_image_path, cwd))
        os.system("docker run -it --rm  %s" % test_image_repo)
    except Exception, e:
        log.red("Failed to test with docker, because of %s" % e.message)


def publish(publish_image_name=None):
    application_conf = ApplicationConf.parse_application_conf() or {}
    if publish_image_name == None:
        publish_image_name = application_conf.get("publish_image_name")
        if publish_image_name == None:
            ques = [
                inquirer.Text('publish_image_name', message="Please input your remote image repo name and tag"),
            ]
            answers = inquirer.prompt(ques)
            ApplicationConf.update_application_conf(answers)
            publish_image_name = answers.get("publish_image_name")

    try:
        cwd = os.getcwd()
        dockerfile_path = os.path.join(cwd, "Dockerfile")
        os.system("docker build -t %s -f %s %s" % (publish_image_name, dockerfile_path, cwd))
        os.system("docker push %s" % publish_image_name)
    except Exception, e:
        log.red("Failed to run with docker,because of %s" % e.message)


def serve():
    application_conf = ApplicationConf.parse_application_conf()
    publish_image_name = application_conf.get("publish_image_name")
    cwd = os.getcwd()
    try:
        publish(publish_image_name)
        if os.path.exists(cwd,"docker-compose.yml") != True:
            construct_compose_file()
        os.system("docker-compose up")
    except Exception, e:
        log.red("Failed to run with docker,because of %s" % e.message)


def construct_compose_file():
    pass
    # ques = [
    #     inquirer.Text('port', message="Please input your expose port"),
    #     inquirer.Text('volume', message="Please input volume mount mapping"),
    # ]
    # answers = inquirer.prompt(ques)
    # application_conf = ApplicationConf.parse_application_conf()

