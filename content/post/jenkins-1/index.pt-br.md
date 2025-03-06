+++
title = "Primeiros Passos com Pipelines Declarativos no Jenkins"
description = "Minha abordagem para executar pipelines declarativos no Jenkins para construir, testar e implantar uma aplicação Spring Boot de exemplo, usando Docker e algumas integrações úteis como Git e Slack."
date = "2021-10-18"
draft = false
toc = false
categories = ["jenkins"]
tags = ["jenkins"]
image = "Jenkins-logo-001.svg"
+++

Depois de horas e horas de treinamento, vídeos, documentação e tutoriais, era hora de colocar em prática os conceitos que aprendi sobre Jenkins, uma das ferramentas de automação mais usadas para CI/CD.
<!--more--->

É sabido que existem muitas outras soluções mais modernas hoje em dia, como GitHub Actions ou Gitlab CI, por exemplo, que é uma abordagem comum, já que você pode aproveitar o SCM (Source Code Management, ou Gerenciamento de Código Fonte) diretamente para automatizar suas tarefas, em vez de depender de uma ferramenta externa. No entanto, o Jenkins ainda é amplamente adotado e você pode executar muitas tarefas de automação sem muito esforço usando-o. Tudo vai depender da situação, do projeto atual e da equipe.
Tradicionalmente, os jobs do Jenkins eram criados usando a interface do usuário do Jenkins e eram chamados de jobs FreeStyle. No Jenkins 2.0, uma nova forma foi introduzida usando uma técnica chamada pipeline como código, onde os jobs são criados usando um arquivo de script contendo os passos a serem executados. Esse arquivo de script é chamado de Jenkinsfile. Isso é apenas uma pincelada sobre os pipelines do Jenkins, há muito mais profundidade nisso e você sempre pode se aprofundar usando a documentação oficial em https://www.jenkins.io/doc/book/pipeline/.

Antes de começarmos a entrar nas coisas sérias, deixe-me apenas mencionar uma referência que inevitavelmente me veio à mente quando li pela primeira vez o nome "Jenkins", que tenho certeza de que a maioria dos gamers do início dos anos 2000 vão se lembrar:

![leeroy_jenkins](leeroy-jenkins-civil-war-pn.jpg)

### 1. O que é um Pipeline de CI/CD?
Um pipeline de CI/CD é geralmente descrito como os processos e estágios de automação na entrega de software. Geralmente, existe uma ferramenta específica usada para realizar isso, que se orquestra com o SCM e as outras ferramentas. Ele pode ser usado para construir código, executar testes unitários, testes de fumaça (smoke tests), chamar ferramentas externas como SonarQube, Anchore, Trivy, construir imagens Docker e implantar em ambientes como Kubernetes ou onde quer que a aplicação seja entregue. Ao realizar operações e testes padronizados, um pipeline de CI/CD pode ajudar a reduzir erros manuais, fornecer feedback aos desenvolvedores e permitir iterações rápidas.

### 2. O que é um Jenkinsfile?
Um `Jenkinsfile` é apenas um arquivo de texto, geralmente commitado juntamente com o código fonte do projeto em um SCM. Idealmente, cada aplicação terá seu Jenkinsfile.
Um Jenkinsfile pode ser escrito de duas maneiras - "sintaxe de pipeline com script" ou "sintaxe de pipeline declarativa".

### 3. O que é um Pipeline Scripted do Jenkins?
Pipelines com script são executados no Jenkins master com a ajuda de um executor leve. Ele usa muito poucos recursos para traduzir o pipeline em comandos atômicos. Tanto a sintaxe declarativa quanto a sintaxe com script são diferentes uma da outra e são definidas de forma diferente. Pipelines com script são escritos em Groovy.

- Requer conhecimento da linguagem Groovy;
- O Jenkinsfile começa com a palavra 'node';
- Capacidades avançadas;
- Motor Groovy;
- Pode conter construções de programação padrão, como bloco if-else, bloco try-catch, etc.

Um exemplo de um Pipeline Scripted:

```groovy
node {
    stage('Build') {
        if (env.BRANCH_NAME == 'master') {
            echo "Estou na branch master, construindo a aplicação"
            bat "msbuild ${C:\\Jenkins\\my_project\\workspace\\test\\my_project.sln}"
        } else {
            echo 'Em direção ao centro do Computador Nuvem.'
        }
    }
    stage('Selenium') {
        echo 'Executando Testes de Fumaça do Selenium'
        dir(bachelol) {  //muda o caminho para “bachelol”
            bat "mvn clean test -Dsuite=SMOKE_TEST -Denvironment=QA"
        }
    }
}
```

### 4. O que é um Pipeline Declarativo do Jenkins?

O Pipeline Declarativo é relativamente novo e fornece uma sintaxe simplificada e opinativa sobre os subsistemas do Pipeline. Sua sintaxe oferece uma maneira fácil de criar pipelines. Ele contém uma hierarquia predefinida e oferece a capacidade de controlar todos os aspectos da execução de um pipeline de maneira simples e direta.

- A adição mais recente na técnica de criação de job pipeline do Jenkins;
- Precisa usar as construções predefinidas para criar pipelines; Portanto, não é tão flexível quanto um pipeline com script;
- O Jenkinsfile começa com a palavra 'pipeline' e existe uma estrutura predefinida;
- Normalmente, a maneira preferida de começar, pois oferecem um rico conjunto de recursos, vêm com uma curva de aprendizado menor e não exigem o aprendizado prévio de uma linguagem de programação como Groovy apenas para escrever código de pipeline;
- Também podemos validar a sintaxe do código do pipeline declarativo antes de executar o job. Ajuda a evitar muitos problemas de tempo de execução com o script de build.

### 5. Por que executar o Jenkins no Docker?

Apesar das vantagens inerentes (e ressalvas) de executar qualquer coisa no Docker, os principais motivos que pude pensar são:

- Capacidade de manter a configuração do servidor sob controle de versão;
- Executar várias cópias do servidor em qualquer lugar;
- Integrar com Kubernetes e outras plataformas de orquestração;
- A imagem oficial do Docker do Jenkins é amplamente adotada e mantida;
- Implementação simples = administração simples.

O principal (Desvantagem|Ressalva|Problema|Questão|Falha) é quando você também deseja usar agentes com o docker. Para fazer isso, você precisará de alguma implementação do Docker in Docker. Existem algumas maneiras de fazer isso, mas as duas maneiras mais fáceis são conectar o contêiner Jenkins diretamente ao socket Docker do host usando `-v /var/run/docker.sock:/var/run/docker.sock` e alterar as permissões, ou habilitar o TCP no lado do servidor Docker.
Se você puder executar seu servidor Jenkins no Kubernetes, poderá habilitá-lo para iniciar novos pods de agente dentro do cluster, o que oferece ainda mais flexibilidade. Vou tentar isso no futuro, já que estou sem créditos na AWS e meu cluster de desenvolvimento está atrás de um proxy, o que é uma dor de cabeça para lidar.

### 6. Construindo uma Imagem do Jenkins

O `Dockerfile` abaixo cria uma imagem baseada no Jenkins LTS mais recente do Dockerhub e pré-instala os plugins necessários:

```dockerfile
FROM jenkins/jenkins:lts

# Ignorar o assistente de configuração
ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false"

# Definir o grupo docker
ARG DOCKER_GID=998

# Obter plugins
RUN /usr/local/bin/install-plugins.sh \
  workflow-multibranch:latest \
  pipeline-model-definition:latest \
  pipeline-stage-view:latest \
  git:latest \
  credentials:latest \
  slack:latest

# Instalar Docker & docker-compose
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

Eu me referi à documentação oficial:
https://docs.docker.com/compose/install/
https://docs.docker.com/engine/install/ubuntu/

Para subir uma instância do Jenkins na minha máquina local, usei um arquivo `docker-compose.yml` e coloquei tudo na mesma pasta. O serviço jenkins aponta para um dockerfile no mesmo caminho e o contêiner estará acessível em `localhost:9080`. Mapeei o `docker.sock` para o contêiner e combinei o docker GID com o host, e também criei e mapeei uma pasta `jenkins_home` localmente para persistir os dados:

```yaml
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

Agora que temos uma instância do Jenkins em execução com os plugins instalados e com acesso ao dockerd do host, vamos começar a usá-lo para automatizar um build.

### 7. A Aplicação de Exemplo Spring PetClinic

Para testar tudo, baixei a "Spring PetClinic Sample Application" (pode ser encontrada aqui: https://github.com/spring-projects/spring-petclinic), que é escrita em Java usando Spring Boot e construída com Maven. Se você clonar o repositório oficial, você terá um Maven Wrapper incluído que pode ser usado para construir a aplicação. Então, antes de tentar automatizar qualquer coisa com Jenkins, vamos primeiro construir, testar e executar a aplicação manualmente:

```bash
# Clonar o repo
git clone https://github.com/spring-projects/spring-petclinic.git

# Entrar no diretório
cd spring-petclinic

# Construir a aplicação
./mvnw package

# Executar a aplicação
java -jar target/*.jar
```

Na primeira vez que executei o comando `mvnw package`, demorou um pouco para terminar, pois baixou todas as dependências. Depois disso, as execuções subsequentes levaram cerca de um minuto para terminar. Isso é praticamente tudo que temos que fazer para testar se ele constrói e executa corretamente, eu apenas segui as instruções do repositório sem mudar nada. Se ele executar, sabemos que o código deve funcionar dentro do pipeline também. As mudanças virão quando usarmos o Maven do Jenkins e tentarmos executar os testes JUnit.

Saída do build:
```
[INFO] Construindo jar: ./github/spring-petclinic/target/spring-petclinic-2.5.0-SNAPSHOT.jar
[INFO]
[INFO] --- spring-boot-maven-plugin:2.5.4:repackage (repackage) @ spring-petclinic ---
[INFO] Substituindo o artefato principal pelo arquivo repaginado
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Tempo total: 01:15 min
[INFO] Finalizado em: 2021-10-19T11:35:43-03:00
[INFO] ------------------------------------------------------------------------
```
Saída de `java -jar target/*.jar`:
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

### 8. Usando Maven no Jenkins

Existem algumas maneiras diferentes de usar o Maven com o Jenkins. Existe um plugin Maven para Jenkins, e podemos instalar o Maven no servidor Jenkins e configurá-lo em "Global Tool Configuration". Como queremos usar contêineres docker como executores ou agentes, essa não seria uma opção. Também poderíamos usar o wrapper que vem com o projeto, mas uma rota melhor e simples seria usar a imagem oficial do Maven docker, e dessa forma podemos ter um agente sempre atualizado e completamente separado do Maven do nosso servidor Jenkins. Essa abordagem facilita o gerenciamento do ambiente e também permite que um único servidor Jenkins trabalhe com diferentes tipos de builds com uma única instalação, sem ter que incorporar todas as ferramentas usadas no servidor.

Eu construí um pipeline com seis estágios: **Init**, **Build**, **Test** e **Build Image**, **Publish Image** e **Prod**. Alguns dos principais aspectos são:

- Ele monta o diretório m2, que é usado pelo maven, localmente para ter cache entre os builds, e também o settings.xml para permitir a configuração de parâmetros personalizados para o Maven;
- A Imagem Docker Maven 3.8.3 com AdoptOpenJDK 11 é usada como um agente apenas para os estágios que a requerem;
- As credenciais do Dockerhub foram adicionadas anteriormente no Jenkins.

```groovy
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
                echo "Implantando para ${DEPLOY_TO}"
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
                echo 'Algum passo extra quando no release de produção'
            }
        }
    }
}
```

Eu usei o Plugin Slack para integrar com o Jenkins, seguindo [esta](https://github.com/jenkinsci/slack-plugin) documentação. Usei apenas duas variáveis apenas para ilustrar o que pode ser enviado como mensagem, mas uma lista completa de variáveis de ambiente pode ser encontrada diretamente no Jenkins acessando `http://localhost:9080/env-vars.html`. Claro, você tem que mudar `localhost:9080` para o endereço do seu servidor.

O estágio **Init** imprime as versões das principais ferramentas utilizadas, úteis para depurar problemas;

O estágio **Build** executa `mvn package`, que cria os arquivos jar;

O estágio **Test** executa os testes unitários. O Spring Pet Clinic tem um total de 40 testes configurados, e isso dependeria de como a equipe de desenvolvimento criou seus testes;

O estágio **Build Image** cria uma imagem Docker e a publica no Dockerhub;

O estágio **Publish Image** publica a imagem no Dockerhub;

O estágio **Prod** não faz nada, é apenas um exemplo de um passo condicional que pode ser executado dependendo de uma variável.

Observe que não há um estágio para clonar o repositório no início; esse estágio é **implícito** quando você configura o Jenkins para puxar o pipeline do SCM, que é o plano aqui.

Aqui está o Dockerfile que eu usei para publicar a aplicação:

```dockerfile
FROM openjdk:11-jre-slim

RUN groupadd --gid 1000 java \
  && useradd --uid 1000 --gid java --shell /bin/bash --create-home java

USER java

VOLUME /tmp

WORKDIR /app

COPY --chown=java:java ./target/*.jar /app/

CMD ["java","-Djava.security.egd=file:/dev/./urandom","-jar","/app/*.jar"]
```

Esse é um pipeline funcional, e eu queria incluir a maioria dos conceitos que vi nos cursos. Existem outros recursos que gostaria de experimentar no futuro, como bibliotecas compartilhadas e pipelines multi-branch, mas isso pode entrar em outro post.

### 9. Cursos que eu fiz ou recomendo:

##### a. Jenkins, Do Zero ao Herói: Torne-se um Mestre DevOps Jenkins
Udemy, por Ricardo Andre Gonzalez Gomez, 2018
https://www.udemy.com/course/jenkins-from-zero-to-hero/

Eu achei este curso um pouco desatualizado e parece que o autor parou de mantê-lo em 2020. No entanto, se você nunca usou o Jenkins antes e quer um curso barato para começar, eu recomendo fortemente este. Também é bem recomendado em muitas outras fontes e tem uma alta taxa na Udemy. Ricardo se concentra muito em Docker, então pode ser mais adequado para alguém sem nenhuma experiência em Docker também.

##### b. Integração Contínua com Jenkins
Pluralsight, por diferentes autores, atualizado constantemente
https://app.pluralsight.com/paths/skill/continuous-integration-with-jenkins

A Pluralsight tem um total de 8 cursos, cada um com cerca de 2 horas de duração, o que torna o Skill Path do Jenkins. Fiz quatro deles durante a última Pluralsight Free Week e, como outros cursos que fiz na Pluralsight, a qualidade foi muito superior. Infelizmente, a Pluralsight custa uma grande quantia de dinheiro, então geralmente fico de olho em suas semanas gratuitas e fins de semana gratuitos periodicamente. O bom é que você pode baixar o material do curso e a maioria dos autores tem repositórios no GitHub onde você pode verificar o código mais tarde.

### 10. Referências

https://stackoverflow.com/questions/44440164/what-are-the-advantages-of-running-jenkins-in-a-docker-container

https://www.cinqict.nl/blog/building-a-jenkins-development-docker-image

https://tomgregory.com/building-a-spring-boot-application-in-jenkins/

<br>

<b><center>Se você leu até o final, gostaria de ouvir seus comentários, e espero que isso o tenha ajudado de alguma forma.</b></center>

. \
. \
. \
.

<br>
E desculpe pelo post longo... aqui está uma batata.

![potato](222-5c163369f2bfd__880.jpg)
Fonte: [@truth.potato](https://www.instagram.com/truth.potato/?hl=en)