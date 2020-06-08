node {
    dir('src') { checkout scm }
    def userId = sh(returnStdout: true, script: 'id -u').trim()
    docker.build('managarm_buildenv', "--build-arg USER=${userId} src/docker/")
          .inside {
        dir('build') {
            stage('Build system') {
                sh '''#!/bin/sh
                set -xe
                xbstrap init ../src || true
                xbstrap install --all -cu --hard-reset
                '''
            }
        }
        stage('Make docs') {
            dir('docs') {
                sh '''#!/bin/sh
                set -xe
                mkdir -p hel
                sed 's|@ROOTDIR@|../src/managarm/hel|' ../src/managarm/hel/Doxyfile.in > Doxyfile
                doxygen
                '''
            }
            dir('build') {
                    sh 'xbstrap runtool --build=managarm-system ninja mdbook'
            }
        }
    }
}
