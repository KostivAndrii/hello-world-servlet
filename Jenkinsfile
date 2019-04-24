import groovy.json.JsonSlurper
//def findRelease() {

    def response = httpRequest customHeaders: [[name: 'X-JFrog-Art-Api', value: 'AKCp5ccGXKgp571DUjg7FfjTru6n8DyEygjrGCkV5JHgjwBYYnzsyRPFuu8g5v244TdnoXbS4'],[name: 'content-type', value: 'text/plain']], httpMode: 'POST', requestBody: 'items.find({"repo":{"$match":"libs-*-local"},"path":{"$match":"com/geekcap/vmturbo/hello-world-servlet-example/*"},"name":{"$match":"*.war"}}).include("repo","name","path")', responseHandle: 'LEAVE_OPEN', url: 'http://artifactory:8081/artifactory/api/search/aql'
//    def response = httpRequest customHeaders: [[name: 'X-JFrog-Art-Api', value: 'AKCp5ccGT2x3evLXvGmtUTVnUq3toYqx4SR3ZeVrdvTdkY4T56V8edN6kEnNJjvNkhWTf7nn4'],[name: 'content-type', value: 'text/plain']], httpMode: 'POST', requestBody: 'items.find({"repo":{"$match":"libs-*-local"},"path":{"$match":"com/geekcap/vmturbo/hello-world-servlet-example/*"},"name":{"$match":"*.war"}}).include("repo","name","path")', responseHandle: 'LEAVE_OPEN', url: 'http://artifactory:8081/artifactory/api/search/aql'
//    def response = httpRequest customHeaders: [[name: 'X-JFrog-Art-Api', value: 'AKCp5ccGT2x3evLXvGmtUTVnUq3toYqx4SR3ZeVrdvTdkY4T56V8edN6kEnNJjvNkhWTf7nn4'],[name: 'content-type', value: 'text/plain']], httpMode: 'POST', requestBody: 'items.find({"repo":{"$match":"libs-*-local"},"path":{"$match":"com/geekcap/vmturbo/hello-world-servlet-example/*"},"name":{"$match":"*.war"}}).include("repo","name","path")', responseHandle: 'LEAVE_OPEN', url: 'http://artifactory:8081/artifactory/api/search/aql'
    def json = new JsonSlurper().parseText(response.content).results.name
    json.add("latest-RELEASE")
    json.add("latest-SNAPSHOT")
//}
pipeline {
    agent any
    parameters {
        choice(choices: json, description: 'Choise artifact', name: 'release')
    } 
/*    triggers {
              pollSCM '* * * * *'
    }*/
    stages {
        stage ('Clone') {
            steps {
                git branch: 'master', url: "https://github.com/KostivAndrii/hello-world-servlet.git"
            }
        } 
/*        stage("Gather Deployment Parameters") {
            steps {
                timeout(time: 30, unit: 'SECONDS') {
                    script {
                        // Show the select input modal
                       def INPUT_PARAMS = input message: 'Please Provide Parameters', ok: 'Next',
                                        parameters: [
                                        choice(name: 'ENVIRONMENT', choices: ['dev','qa'].join('\n'), description: 'Please select the Environment'),
                                        choice(name: 'release', choices: findRelease(), description: 'Choise artifact')]
                        env.ENVIRONMENT = INPUT_PARAMS.ENVIRONMENT
                        env.release = INPUT_PARAMS.release
                    }
                }
            }
        }        */
        stage ('Artifactory configuration') {
            steps {
                rtServer (
                    id: "ARTIFACTORY_SERVER",							// Artifactory1
                    url: "http://192.168.237.125:8081/artifactory",		// SERVER_URL http://192.168.237.125:8081/artifactory
                    credentialsId: "Artifactory_user"  					// CREDENTIALS Artifactory_user
                )
                rtMavenDeployer (
                    id: "MAVEN_DEPLOYER",
                    serverId: "ARTIFACTORY_SERVER",
                    releaseRepo: "libs-release-local",
                    snapshotRepo: "libs-snapshot-local"
                )
                rtMavenResolver (
                    id: "MAVEN_RESOLVER",
                    serverId: "ARTIFACTORY_SERVER",
                    releaseRepo: "libs-release",
                    snapshotRepo: "libs-snapshot"
                )
            }
        }
        stage ('Exec Maven') {
            steps {
                rtMavenRun (
                    tool: "MAVEN_TOOL", // Tool name from Jenkins configuration
                    pom: 'pom.xml',
                    goals: 'clean install',
                    deployerId: "MAVEN_DEPLOYER",
                    resolverId: "MAVEN_RESOLVER"
                )
            }
        }
        stage ('SonarQube') {
            steps {
                echo 'Hello, SonarQube'
                sh 'mvn --version'
                sh "mvn clean package sonar:sonar"
            }
        }
        stage ('Publish build info') {
            steps {
                rtPublishBuildInfo (
                    serverId: "ARTIFACTORY_SERVER"
                )
            }
        }
        stage ('Download war from artifactory') {
            steps {
                echo 'Download war from artifactory'
                echo "Trying: ${params.release}"
            }
        }
        stage ('Deploy AWS') {
            steps {
                echo 'Hello, AWS'
                sh 'pwd'
                sh 'ls -la'
                sh './aws_ec2.sh ${release}'
            }
        }      
    }
}
