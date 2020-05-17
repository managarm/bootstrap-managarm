node {
    cleanWs()
    dir('src') { checkout scm }
    def userId = sh(returnStdout: true, script: 'id -u').trim()
    docker.build('managarm_buildenv', "--build-arg USER=${userId} src/docker/")
          .inside {
        dir('build') {
            sh 'cp ../src/ci/pipeline.yml .'
            sh 'xbstrap init ../src || true'
            jobs = sh(returnStdout: true, script: 'xbstrap-pipeline compute-graph --linear').split('\n')
            any_failures = false
            for(job in jobs) {
                try {
                    stage(job) {
                        sh('xbstrap-pipeline run-job --keep-going ' + job)
                    }
                } catch(e) {
                    any_failures = true
                }
            }
            if(any_failures)
                sh 'exit 1' // Raise some error.

            stage('Install packages') {
                sh 'xbstrap install --all --only-wanted --keep-going'
            }

            stage('Archive packages') {
                sh '''#!/bin/sh
                set -xe
                for pkg in `xbstrap list-pkgs`; do
                    if [ -d packages/$pkg ]; then
                        xbstrap archive $pkg
                    fi
                done
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
