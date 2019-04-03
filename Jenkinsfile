pipeline {
    agent any
    environment {
        def mvnHome
      //   commitId = gitUtils.getCommitId()
      //   credentialsId = 'svc_icinga-bitbucket'
      //   imageName = "prom/automic-exporter:build-${env.BUILD_ID}"
      //   imageRepo = "tools.adidas-group.com:5000"
    }
    stages {
         stage('Preparation') { // for display purposes
            // Get some code from a GitHub repository
            git 'https://github.com/ligado/hello-world-servlet.git'
            // Get the Maven tool.
            // ** NOTE: This 'M3' Maven tool must be configured
            // **       in the global configuration.
            mvnHome = tool 'M3'
         }
         stage ('Artifactory configuration') {
            steps {
                  rtServer (
                     id: "192_168_237_125",
                     url: "http://192.168.237.125:8081/artifactory",
                     // {{ jenkins_home }}/credentials.xml
                     credentialsId: artifactory_192_168_237_125
                  )
                  rtMavenDeployer (
                     id: "M3_DEPLOYER",
                     serverId: "192_168_237_125",
                     releaseRepo: "libs-release-local",
                     snapshotRepo: "libs-snapshot-local"
                  )
                  rtMavenResolver (
                     id: "M3_RESOLVER",
                     serverId: "192_168_237_125",
                     releaseRepo: "libs-release",
                     snapshotRepo: "libs-snapshot"
                  )
            }
         }
         stage ('Exec Maven') {
            steps {
                  rtMavenRun (
                     tool: 'M3', // Tool name from Jenkins configuration
                     pom: 'pom.xml',
                     goals: '-Dmaven.test.failure.ignore clean package',
                     deployerId: "M3_DEPLOYER",
                     resolverId: "M3_RESOLVER"
                  )
            }
         }
         stage('Results') {
            junit '**/target/surefire-reports/TEST-*.xml'
            archive 'target/*.jar'
         }
         stage ('Publish build info') {
            steps {
                  rtPublishBuildInfo (
                     serverId: "192_168_237_125"
                  )
            }
         }

         stage('Build') {
            // Run the maven build
            if (isUnix()) {
               sh "'${mvnHome}/bin/mvn' -Dmaven.test.failure.ignore clean package"
            } else {
               bat(/"${mvnHome}\bin\mvn" -Dmaven.test.failure.ignore clean package/)
            }
         }
    }
}

