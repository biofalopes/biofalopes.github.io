+++
title = "Getting started with Jenkins Declarative Pipelines"
description = "My approach on running declarative pipelines on Jenkins to build, test and deploy a sample springboot application, using Docker and some useful integrations like Git and Slack."
date = "2021-10-18"
draft = false
toc = false
categories = ["jenkins"]
tags = ["jenkins"]
image = "Jenkins-logo-001.svg"
+++

After hours and hours of training, videos, documentation, and tutorials, it was time to put into practice the concepts I learned about Jenkins, one of the most used automation tools for CI/CD. 
<!--more--->  

It is known that there are many other more modern solutions today, like GitHub Actions or Gitlab CI, for instance, which is a common approach since you can leverage the SCM directly to automate your tasks instead of depending on an external tool. However, Jenkins is still widely adopted and you can perform many automation tasks without much effort using it. It's all going to depend on the situation, the current project, and the team.
Traditionally, Jenkins jobs were created using the Jenkins UI and were called FreeStyle jobs. In Jenkins 2.0, a new way was introduced using a technique called pipeline as code, where jobs are created using a script file containing the steps to be executed. That scripted file is called Jenkinsfile. That's just a glimpse on Jenkins pipelines, there's much more depth to it and you can always dive deeper using the official documentation at https://www.jenkins.io/doc/book/pipeline/.

Before we start to get into the real stuff, let me just mention a reference that inevitably came into my mind when I first read the name "Jenkins", which I'm sure that most gamers from early 2000s are gonna remember:

![leeroy_jenkins](leeroy-jenkins-civil-war-pn.jpg)

If you'd like to watch the video, here's the YouTube link to it: [Leeroy Jenkins HD 1080p](https://www.youtube.com/watch?v=mLyOj_QD4a4&t=4s)

Alright, let’s start with the basics.

### 1. What's a CI/CD Pipeline?
A CI/CD pipeline is usually described as the processes and stages of automation on software delivery. There's usually a specific tool used to achieve this, that orchestrates with SCM and the other tools. It can be used to build code, run unit tests, smoke tests, call external tools like SonarQube, Anchore, Trivy, build Docker images and deploy to environments like Kubernetes or wherever the application is delivered. By performing standardized operations and tests, a CI/CD pipeline can help reduce manual errors, provide feedback to developers, and allow fast iterations.

### 2. What's a Jenkinsfile?
A `Jenkinsfile` is just a text file, usually checked in along with the project's source code in an SCM. Ideally, each application will have its  Jenkinsfile.
A Jenkinsfile can be written in two ways - "scripted pipeline syntax" or "declarative pipeline syntax".

### 3. What's a Jenkins Scripted Pipeline?
Scripted pipelines run on the Jenkins master with the help of a lightweight executor. It uses very few resources to translate the pipeline into atomic commands. Both declarative and scripted syntax are different from each other and are defined differently. Scripted pipelines are written in Groovy.

- It requires knowledge of the Groovy language;
- The Jenkinsfile starts with the word 'node';
- Advanced cabapilities;
- Groovy engine;
- Can contain standard programming constructs like if-else block, try-catch block, etc.

An example of a Scripted Pipeline:

```
node {
    stage('Build') {
        if (env.BRANCH_NAME == 'master') {
            echo "I'm on master brand, building application"
            bat "msbuild ${C:\\Jenkins\\my_project\\workspace\\test\\my_project.sln}"
        } else {
            echo 'Towards the center of the Cloud Computer.'
        }
    }
    stage('Selenium') {
        echo 'Running Selenium Smoke Tests'
        dir(bachelol) {  //changes the path to “bachelol”
            bat "mvn clean test -Dsuite=SMOKE_TEST -Denvironment=QA"
        }  
    }
}
```

###  4. What's a Jenkins Declarative Pipeline?

The Declarative Pipeline is relatively new and provides a simplified, opinionated syntax on top of the Pipeline subsystems. Its syntax offers an easy way to create pipelines. It contains a predefined hierarchy and gives you the ability to control all aspects of a pipeline execution in a simple, straightforward manner.

- The latest addition in Jenkins pipeline job creation technique;
- Needs to use the predefined constructs to create pipelines; Hence, it is not flexible as a scripted pipeline;
- The Jenkinsfile starts with the word 'pipeline', and there is a predefined structure;
- Usually, the preferred way to start, as they offer a rich set of features, come with less learning curve & no prerequisite to learn a programming language like Groovy just for the sake of writing pipeline code;
- We can also validate the syntax of the Declarative pipeline code before running the job. It helps to avoid a lot of runtime issues with the build script.

###  5. Why run Jenkins on Docker?

Despite the inherent advantages (and caveats) of running anything in Docker, the main reasons I could think of are:

- Ability to keep the server configuration under version control;
- Run multiple copies of the server anywhere;
- Integrate with Kubernetes and other orchestration platforms;
- Jenkins' official Docker image is widely adopted and maintained;
- Simple implementation = simple administration.

The main (Drawback|Caveat|Problem|Issue|Flaw) is when you want to use agents with docker too. To do that you're gonna need some implementation of Docker in Docker. There are a few ways to do that, but the two easiest ways are connecting the Jenkins container directly to the host's Docker socket using `-v /var/run/docker.sock:/var/run/docker.sock` and changing the permissions, or enabling TCP on the Docker server-side. \
If you can run your Jenkins server on Kubernetes, you can enable it to launch new agent pods inside the cluster which gives you even more flexibility. I'll try that in the future since I'm out of credits on AWS and my dev cluster is behind a proxy, which is a real pain to deal with.

### 6. Building a Jenkins Image

The `Dockerfile` below creates an image based on the latest Jenkins LTS from Dockerhub, and preinstalls the plugins needed:

```
FROM jenkins/jenkins:lts

# Skip setup wizard
ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false"

# Set docker group
ARG DOCKER_GID=998

# Get plugins
RUN /usr/local/bin/install-plugins.sh \
  workflow-multibranch:latest \
  pipeline-model-definition:latest \
  pipeline-stage-view:latest \
  git:latest \
  credentials:latest \
  slack:latest

# Install Docker & docker-compose
USER root

RUN apt-get update && \
    apt-get -y install apt-transport-https \
      ca-certificates \
      curl \
      gnupg2 \
      software-properties-common && \
    curl -fsSL https://download.docker.com/linux/$(. /etc/os-release; echo "$ID")/gpg > /tmp/dkey; apt-key add /tmp/dkey && \
    add-apt-repository \
      "deb [arch=amd64] https://download.docker.com/linux/$(. /etc/os-release; echo "$ID") \
      $(lsb_release -cs) \
      stable" && \
    apt-get update && \
    groupadd -g ${DOCKER_GID} docker && \
    apt-get -y install docker-ce docker-ce-cli containerd.io

RUN curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && chmod +x /usr/local/bin/docker-compose

RUN usermod -aG docker jenkins 

USER jenkins
```

I referred to the official documentation: \
https://docs.docker.com/compose/install/ \
https://docs.docker.com/engine/install/ubuntu/

To spin up a Jenkins instance on my local machine, I used a `docker-compose.yml` file and put everything on the same folder. The jenkins service points to a dockerfile on the same path, and the container will be accessible on `localhost:9080`. I mapped the `docker.sock` to the container and matched the docker GID with the host, and also created and mapped a `jenkins_home` folder locally to persist data:

```
version: "3.8"
services:
  jenkins:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
    - "127.0.0.1:9080:8080"
    volumes:
    - ./jenkins_home:/var/jenkins_home
    - /var/run/docker.sock:/var/run/docker.sock
    restart: unless-stopped
```

Now that we have a running Jenkins instance with the plugins installed and with access to the host's dockerd, let's start using it to automate a build.

### 7. The Spring PetClinic Sample Application

To test everything, I downloaded the "Spring PetClinic Sample Application" (can be found here: https://github.com/spring-projects/spring-petclinic), which is written in Java using Spring Boot and built with Maven. If you clone the official repository, you'll get a Maven Wrapper bundled together that can be used to build the application. So before trying to automate anything with Jenkins, let's first build, test, and run the application manually:

```
# Clone the repo
git clone https://github.com/spring-projects/spring-petclinic.git

# Enter the directory
cd spring-petclinic

#Build the application
./mvnw package

#Run the application
java -jar target/*.jar
```

The first time I ran the `mvnw package` command, it took a while to finish since it downloaded all the dependencies. After that, subsequent runs took around a minute to finish. That's pretty much all we have to do to test if it builds and runs properly, I just followed the instructions from the repository without changing anything. If it runs, we know that the code should work inside the pipeline too. The changes will come when we use the Maven from Jenkins and try to run JUnit tests.

Output from the build:
```
[INFO] Building jar: ./github/spring-petclinic/target/spring-petclinic-2.5.0-SNAPSHOT.jar
[INFO] 
[INFO] --- spring-boot-maven-plugin:2.5.4:repackage (repackage) @ spring-petclinic ---
[INFO] Replacing main artifact with repackaged archive
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  01:15 min
[INFO] Finished at: 2021-10-19T11:35:43-03:00
[INFO] ------------------------------------------------------------------------
```
Output from `java -jar target/*.jar`:
```
java -jar target/*.jar


              |\      _,,,--,,_
             /,`.-'`'   ._  \-;;,_
  _______ __|,4-  ) )_   .;.(__`'-'__     ___ __    _ ___ _______
 |       | '---''(_/._)-'(_\_)   |   |   |   |  |  | |   |       |
 |    _  |    ___|_     _|       |   |   |   |   |_| |   |       | __ _ _
 |   |_| |   |___  |   | |       |   |   |   |       |   |       | \ \ \ \
 |    ___|    ___| |   | |      _|   |___|   |  _    |   |      _|  \ \ \ \
 |   |   |   |___  |   | |     |_|       |   | | |   |   |     |_    ) ) ) )
 |___|   |_______| |___| |_______|_______|___|_|  |__|___|_______|  / / / /
 ==================================================================/_/_/_/

:: Built with Spring Boot :: 2.5.4


2021-10-19 11:38:31.201  INFO 39806 --- [           main] o.s.s.petclinic.PetClinicApplication     : Starting PetClinicApplication v2.5.0-SNAPSHOT using Java 11.0.11 on my-machine with PID 39806 (./github/spring-petclinic/target/spring-petclinic-2.5.0-SNAPSHOT.jar started by biofa in ./github/spring-petclinic)
2021-10-19 11:38:31.204  INFO 39806 --- [           main] o.s.s.petclinic.PetClinicApplication     : No active profile set, falling back to default profiles: default
2021-10-19 11:38:32.230  INFO 39806 --- [           main] .s.d.r.c.RepositoryConfigurationDelegate : Bootstrapping Spring Data JPA repositories in DEFAULT mode.
2021-10-19 11:38:32.288  INFO 39806 --- [           main] .s.d.r.c.RepositoryConfigurationDelegate : Finished Spring Data repository scanning in 50 ms. Found 4 JPA repository interfaces.
2021-10-19 11:38:33.020  INFO 39806 --- [           main] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat initialized with port(s): 8080 (http)
2021-10-19 11:38:33.036  INFO 39806 --- [           main] o.apache.catalina.core.StandardService   : Starting service [Tomcat]
2021-10-19 11:38:33.037  INFO 39806 --- [           main] org.apache.catalina.core.StandardEngine  : Starting Servlet engine: [Apache Tomcat/9.0.52]
2021-10-19 11:38:33.128  INFO 39806 --- [           main] o.a.c.c.C.[Tomcat].[localhost].[/]       : Initializing Spring embedded WebApplicationContext
2021-10-19 11:38:33.128  INFO 39806 --- [           main] w.s.c.ServletWebServerApplicationContext : Root WebApplicationContext: initialization completed in 1865 ms
2021-10-19 11:38:33.377  INFO 39806 --- [           main] com.zaxxer.hikari.HikariDataSource       : HikariPool-1 - Starting...
2021-10-19 11:38:33.590  INFO 39806 --- [           main] com.zaxxer.hikari.HikariDataSource       : HikariPool-1 - Start completed.
2021-10-19 11:38:33.919  INFO 39806 --- [           main] org.ehcache.core.EhcacheManager          : Cache 'vets' created in EhcacheManager.
2021-10-19 11:38:33.934  INFO 39806 --- [           main] org.ehcache.jsr107.Eh107CacheManager     : Registering Ehcache MBean javax.cache:type=CacheStatistics,CacheManager=urn.X-ehcache.jsr107-default-config,Cache=vets
2021-10-19 11:38:33.941  INFO 39806 --- [           main] org.ehcache.jsr107.Eh107CacheManager     : Registering Ehcache MBean javax.cache:type=CacheStatistics,CacheManager=urn.X-ehcache.jsr107-default-config,Cache=vets
2021-10-19 11:38:34.021  INFO 39806 --- [           main] o.hibernate.jpa.internal.util.LogHelper  : HHH000204: Processing PersistenceUnitInfo [name: default]
2021-10-19 11:38:34.081  INFO 39806 --- [           main] org.hibernate.Version                    : HHH000412: Hibernate ORM core version 5.4.32.Final
2021-10-19 11:38:34.204  INFO 39806 --- [           main] o.hibernate.annotations.common.Version   : HCANN000001: Hibernate Commons Annotations {5.1.2.Final}
2021-10-19 11:38:34.332  INFO 39806 --- [           main] org.hibernate.dialect.Dialect            : HHH000400: Using dialect: org.hibernate.dialect.H2Dialect
2021-10-19 11:38:34.955  INFO 39806 --- [           main] o.h.e.t.j.p.i.JtaPlatformInitiator       : HHH000490: Using JtaPlatform implementation: [org.hibernate.engine.transaction.jta.platform.internal.NoJtaPlatform]
2021-10-19 11:38:34.962  INFO 39806 --- [           main] j.LocalContainerEntityManagerFactoryBean : Initialized JPA EntityManagerFactory for persistence unit 'default'
2021-10-19 11:38:36.371  INFO 39806 --- [           main] o.s.b.a.e.web.EndpointLinksResolver      : Exposing 13 endpoint(s) beneath base path '/actuator'
2021-10-19 11:38:36.441  INFO 39806 --- [           main] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat started on port(s): 8080 (http) with context path ''
2021-10-19 11:38:36.453  INFO 39806 --- [           main] o.s.s.petclinic.PetClinicApplication     : Started PetClinicApplication in 5.753 seconds (JVM running for 6.136)
```

### 8. Using Maven on Jenkins

There are a couple of different ways to use Maven with Jenkins. There is a Maven plugin for Jenkins, and we can install Maven on the Jenkins server and set it up at "Global Tool Configuration". Since we want to use docker containers as executors or agents, that would not be an option. We could also use the wrapper that comes with the project, but a better and simple route would be to use the official Maven docker image, and that way we can have an agent always updated and completely separate Maven from our Jenkins server. This approach makes it easier to manage the environment and also allows for a single Jenkins server to work with different types of builds with a single installation, without having to embed every tool used on the server.

I built a pipeline with six stages: **Init**, **Build**, **Test** and **Build Image**, **Publish Image** and **Prod**. Some of the main aspects are:

- It mounts the m2 directory, which is used by maven, locally to have cache between builds, and also settings.xml to enable setting custom parameters to Maven;
- Maven 3.8.3 with AdoptOpenJDK 11 Docker Image is used as an agent only for the stages that require it;
- Dockerhub credentials were added previously on Jenkins.

```
pipeline {
    agent none
    environment {
        DEPLOY_TO = 'staging'
        imageName = "fabioctba/spring-petclinic"
        registryCredential = 'dockerhub'
        dockerImage = ''
    }
    stages {
        stage('Init'){
            agent any
            steps {
                slackSend channel: '#jenkins', message: "${env.BUILD_ID} on ${env.JENKINS_URL} - Starting"
                sh 'git --version'
                echo "Deploying to ${DEPLOY_TO}"
            }
        }
        stage('Build') {
            agent {
                docker {
                    image 'maven:3.8.3-adoptopenjdk-11'
                    args '-v m2:/root/.m2 -v settings.xml:/root/.m2/settings.xml'
                }
            }
            steps {
                slackSend channel: '#jenkins', message: "${env.BUILD_ID} on ${env.JENKINS_URL} - Building"
                sh 'mvn -B -DskipTests clean package'

            }
        }
        stage('Test') {
            agent {
                docker {
                    image 'maven:3.8.3-adoptopenjdk-11'
                    args '-v m2:/root/.m2 -v settings.xml:/root/.m2/settings.xml'
                }
            }
            steps {
                slackSend channel: '#jenkins', message: "${env.BUILD_ID} on ${env.JENKINS_URL} - Running Tests"
                sh 'mvn test' 
            }
            post {
                always {
                    archiveArtifacts artifacts: 'target/*.jar'
                    junit 'target/surefire-reports/*.xml' 
                }
            }
        }
        stage('Build Image') { 
            agent any
            steps {
                slackSend channel: '#jenkins', message: "${env.BUILD_ID} on ${env.JENKINS_URL} - Building Image"

                script {
                    dockerImage = docker.build imageName
                }
            }
        }
        stage('Publish Image') { 
            agent any
            steps {
                slackSend channel: '#jenkins', message: "${env.BUILD_ID} on ${env.JENKINS_URL} - Building Image"

                script {
                    docker.withRegistry( '', registryCredential ) {
                        dockerImage.push("$BUILD_NUMBER")
                        dockerImage.push('latest')
                    }
                }
            }
        }
        stage('Prod') {
            agent any
            when { 
                allOf { 
                    branch 'master'; 
                    environment name: 'DEPLOY_TO', value: 'production'
                } 
            }
            steps {
                slackSend channel: '#jenkins', message: "${env.BUILD_ID} on ${env.JENKINS_URL} - Running Production stage"
                echo 'Some extra step when on production release'
            }
        }
    }
}
```

I used the Slack Plugin to integrate with Jenkins, following [this](https://github.com/jenkinsci/slack-plugin) documentation. I used only two variables just to illustrate what can be sent as a message, but a full list of environment variables can be found directly on Jenkins accessing `http://localhost:9080/env-vars.html`. Of course, you have to change `localhost:9080` to your server's address.

The **Init** stage prints the versions of the main tools used, useful to debug problems;

The **Build** stage runs `mvn package`, which creates the jar files;

The **Test** stage run the Unit tests. Spring Pet Clinic has a total of 40 tests configured, and that would depend on how the dev team created their tests;

The **Build Image** stage creates a Docker image and publishes it to the Dockerhub;

The **Publish Image** stage publishes the image to Dockerhub;

The **Prod** stage doesn't do anything, it's just an example of a conditional step that can be executed depending on a variable.

Notice that there isn't a stage to clone the repository at the beginning; this stage is **implicit** when you configure Jenkins to pull the pipeline from SCM, which is the plan here.

Here's the Dockerfile I used to publish the application:

```
FROM openjdk:11-jre-slim

RUN groupadd --gid 1000 java \
  && useradd --uid 1000 --gid java --shell /bin/bash --create-home java

USER java

VOLUME /tmp

WORKDIR /app

COPY --chown=java:java ./target/*.jar /app/

CMD ["java","-Djava.security.egd=file:/dev/./urandom","-jar","/app/*.jar"]
```

That is a working pipeline, and I wanted to include most of the concepts I saw in the courses. There are other features I'd like to try in the future like shared libraries and multi-branch pipelines, but this might go into a different post.

### 9. Courses I either took or recommend:

##### a. Jenkins, From Zero To Hero: Become a DevOps Jenkins Master
Udemy, by Ricardo Andre Gonzalez Gomez, 2018 \
https://www.udemy.com/course/jenkins-from-zero-to-hero/

I found this course a little outdated and looks like the author stopped maintaining it in 2020. However, if you never used Jenkins before and want a cheap course to start, I strongly recommend this one. It's also well recommended in many other sources and has a high rate at Udemy. Ricardo focuses a lot on Docker, so it might be better targeted to someone without any experience in Docker also.

##### b. Continuous Integration with Jenkins
Pluralsight, by different authors, updated constantly \
https://app.pluralsight.com/paths/skill/continuous-integration-with-jenkins

Pluralsight has a total of 8 courses, each with around 2 hours of duration, which makes the Jenkins Skill Path. I took four of them during the last Pluralsight Free Week and like other courses I took from Pluralsight, the quality was much superior. Unfortunately, Pluralsight costs a great amount of money, so I usually stay on the lookout for their periodically free weeks and free weekends. The good thing is that you can download the course material and most of the authors have GitHub repositories where you can check the code later.

### 10. References

https://stackoverflow.com/questions/44440164/what-are-the-advantages-of-running-jenkins-in-a-docker-container

https://www.cinqict.nl/blog/building-a-jenkins-development-docker-image

https://tomgregory.com/building-a-spring-boot-application-in-jenkins/

<br>

<b><center>If you read it to the end, I'd like to hear your comments, and hope this helped you in some way. Cheers.</b></center>

. \
. \
. \
. 

<br>
And sorry for the long post... here's a potato. 

![potato](222-5c163369f2bfd__880.jpg)
Source: [@truth.potato](https://www.instagram.com/truth.potato/?hl=en)