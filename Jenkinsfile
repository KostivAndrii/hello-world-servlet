pipeline {
    agent any
/*    triggers {
              pollSCM '* * * * *'
    }*/
    stages {
        stage ('Clone') {
            steps {
                git branch: 'master', url: "https://github.com/KostivAndrii/hello-world-servlet.git"
            }
        }
        stage ('Deploy AWS') {
            steps {
                echo 'Hello, AWS'
            }
        }      
    }
}
