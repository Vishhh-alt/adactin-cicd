pipeline {
    agent any

    environment {
        ADACTIN_HOST  = 'adactinhotelapp.com'
        ADACTIN_PORT  = '443'
        ADACTIN_PROTO = 'https'
        JMETER_HOME   = 'C:\\Users\\Vish\\Downloads\\Vish\\apache-jmeter-5.6.3\\apache-jmeter-5.6.3'
        PYTHON        = 'C:\\Users\\Vish\\AppData\\Local\\Python\\bin\\python.exe'
        THREADS       = '5'
        RAMPUP        = '10'
        DURATION      = '120'
        P95_SLA       = '3000'
        JTL_FILE      = "results\\adactin_${BUILD_NUMBER}.jtl"
        REPORT_DIR    = "results\\report_${BUILD_NUMBER}"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Clean Workspace') {
            steps {
                bat """
                    if exist results rmdir /s /q results
                    mkdir results
                """
            }
        }

        stage('Performance Test') {
            steps {
                bat """
                    "%JMETER_HOME%\\bin\\jmeter.bat" ^
                        -n ^
                        -t  jmx\\adactin_booking.jmx ^
                        -Jhost=%ADACTIN_HOST% ^
                        -Jport=%ADACTIN_PORT% ^
                        -Jprotocol=%ADACTIN_PROTO% ^
                        -Jthreads=%THREADS% ^
                        -Jrampup=%RAMPUP% ^
                        -Jduration=%DURATION% ^
                        -l  %JTL_FILE% ^
                        -e  -o %REPORT_DIR% ^
                        -Jjmeter.save.saveservice.print_field_names=true ^
                        -Jjmeter.save.saveservice.data_type=false ^
                        -Jjmeter.save.saveservice.sent_bytes=false ^
                        -Jjmeter.save.saveservice.idle_time=false ^
                        -Jjmeter.save.saveservice.connect_time=false
                """
            }
        }

        stage('Performance Gate') {
            steps {
                bat """
                    "%PYTHON%" scripts\\check_p95.py ^
                        %JTL_FILE% ^
                        %P95_SLA%
                """
            }
        }

        stage('Trend Gate') {
            steps {
                bat """
                    "%PYTHON%" scripts\\check_trend.py ^
                        results ^
                        %JTL_FILE% ^
                        15
                """
            }
        }

    }

    post {
        always {
            perfReport(
                sourceDataFiles:                 "${JTL_FILE}",
                errorFailedThreshold:            100,
                errorUnstableThreshold:          100,
                relativeFailedThresholdPositive: 50
            )
            publishHTML(target: [
                allowMissing:          true,
                alwaysLinkToLastBuild: true,
                keepAll:               true,
                reportDir:             "${REPORT_DIR}",
                reportFiles:           'index.html',
                reportName:            "JMeter Report Build ${BUILD_NUMBER}"
            ])
            archiveArtifacts(
                artifacts:         "${JTL_FILE}",
                fingerprint:       true,
                allowEmptyArchive: true
            )
        }
        success {
            echo 'Performance gate passed. Ready to promote.'
        }
        failure {
            echo 'Performance gate failed. Check console log for details.'
        }
    }
}
