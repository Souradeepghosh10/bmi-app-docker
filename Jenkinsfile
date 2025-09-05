pipeline {
    agent {
        label 'ec2'
    }

    stages { //stages =- "collection of jobs/stage/task == pipeline"
        stage('Download/clone the source repo from github') { //stage == job == task //job1
            steps { // each job/task can have have multiple steps
               git branch: 'main', url: 'https://github.com/Souradeepghosh10/bmi-app-docker.git'
            }
        }
        stage("Install pip3"){ //job2
            steps{
                sh "yum install python3-pip -y"
        }
        }
        stage("Install dependencies"){ //job3
            steps{
                sh "pip3 install -r requirements.txt"
        }
        }
       
        stage("Build Docker Image"){ //job5
            steps{
                sh "docker build -t mywebimg:latest ."
        }
        }
        stage("Run Docker Container"){ //job6
            steps{
                sh "docker rm -f webos"
                sh "docker run -dit --name webos -p 5000:5000 mywebimg"
        }
        }
        stage("succesfull deployment"){ //job7
            steps{
                echo "Application Deployed Successfully"
        }
        }
    }
}