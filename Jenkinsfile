
pipeline {
    agent any

    options {
        timestamps()
        skipDefaultCheckout(true)
    }

    environment {
        COMPOSE_EXE = 'C:\\Users\\Atul_Raut\\AppData\\Local\\Programs\\DockerDesktop\\resources\\cli-plugins\\docker-compose.exe'
    }

    stages {
        stage('Checkout Project') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                bat 'python -m pip install -r requirements.txt'
            }
        }

        stage('Start Selenium Grid') {
            steps {
                bat '"%COMPOSE_EXE%" up -d'
                bat 'python wait_grid.py'
                bat '"%COMPOSE_EXE%" ps'
                bat 'if not exist reports mkdir reports'
            }
        }

        stage('Cross-Browser Tests') {
            parallel {
                stage('Chrome Tests') {
                    steps {
                        withEnv([
                            'BROWSER=chrome',
                            'SCREENSHOT_DIR=screenshots/chrome'
                        ]) {
                            bat 'python -m pytest -v test_booking.py --junitxml=reports/chrome.xml'
                        }
                    }
                    post {
                        always {
                            junit(
                                testResults: 'reports/chrome.xml',
                                allowEmptyResults: true
                            )
                        }
                    }
                }

                stage('Firefox Tests') {
                    steps {
                        withEnv([
                            'BROWSER=firefox',
                            'SCREENSHOT_DIR=screenshots/firefox'
                        ]) {
                            bat 'python -m pytest -v test_booking.py --junitxml=reports/firefox.xml'
                        }
                    }
                    post {
                        always {
                            junit(
                                testResults: 'reports/firefox.xml',
                                allowEmptyResults: true
                            )
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts(
                artifacts: 'screenshots/**/*.png,reports/*.xml',
                allowEmptyArchive: true,
                fingerprint: true
            )
            bat '"%COMPOSE_EXE%" down -v'
        }
    }
}
