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
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Performance Test') {
            steps {
                bat """
                    if not exist results mkdir results
                    "%JMETER_HOME%\\bin\\jmeter.bat" ^
                        -n ^
                        -t  jmx\\adactin_booking.jmx ^
                        -Jhost=%ADACTIN_HOST% ^
                        -Jport=%ADACTIN_PORT% ^
                        -Jprotocol=%ADACTIN_PROTO% ^
                        -Jthreads=%THREADS% ^
                        -Jrampup=%RAMPUP% ^
                        -Jduration=%DURATION% ^
                        -l  results\\adactin_%BUILD_NUMBER%.jtl ^
                        -e  -o results\\report_%BUILD_NUMBER% ^
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
                        results\\adactin_%BUILD_NUMBER%.jtl ^
                        %P95_SLA%
                """
            }
        }

        stage('Trend Gate') {
            steps {
                bat """
                    "%PYTHON%" scripts\\check_trend.py ^
                        results ^
                        results\\adactin_%BUILD_NUMBER%.jtl ^
                        15
                """
            }
        }

    }

    post {
        always {
            perfReport(
                sourceDataFiles:                 "results\\adactin_${BUILD_NUMBER}.jtl",
                errorFailedThreshold:            0.5,
                errorUnstableThreshold:          0.1,
                relativeFailedThresholdPositive: 20
            )
            publishHTML(target: [
                allowMissing:          true,
                alwaysLinkToLastBuild: true,
                keepAll:               true,
                reportDir:             "results\\report_${BUILD_NUMBER}",
                reportFiles:           'index.html',
                reportName:            "JMeter Report Build ${BUILD_NUMBER}"
            ])
            archiveArtifacts(
                artifacts:             'results/*.jtl',
                fingerprint:           true,
                allowEmptyArchive:     true
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
