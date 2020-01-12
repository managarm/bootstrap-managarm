node {
    cleanWs()
    dir('src') { checkout scm }
    def userId = sh(returnStdout: true, script: 'id -u').trim()
    docker.build('managarm_buildenv', "--build-arg USER=${userId} src/docker/")
          .inside {
        dir('build') {
            stage('Build system') {
                sh '''#!/bin/sh
                set -xe
                xbstrap init ../src || true
                xbstrap install --all
                '''
            }
            stage('Archive packages') {
                sh 'xbstrap archive --all'
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
        }
    }

    stage('Make image') {
        dir('build') {
            sh '''#!/bin/sh
            set -xe
            xzcat /var/local/image-2gib.xz > image
            ../src/scripts/prepare-sysroot
            ../src/scripts/mkimage
            xz --fast image
            '''
        }
    }

    stage('Collect results') {
        sh 'rsync -av --delete docs/hel/doc/html/ /var/www/docs'
        sh 'rsync -av --delete build/packages/*.tar.gz build/image.xz /var/www/pkgs/nightly'
        archiveArtifacts 'build/packages/*.tar.gz,build/image.xz'
    }
}
