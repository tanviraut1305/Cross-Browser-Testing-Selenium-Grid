
pipeline {
    agent any

    options {
        timestamps()
        skipDefaultCheckout(true)
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
                bat 'docker compose up -d'
                bat 'python wait_grid.py'
                bat 'docker compose ps'
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
            bat 'docker compose down -v'
        }
    }
}
