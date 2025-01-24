ENV['VAGRANT_DEFAULT_PROVIDER'] = 'docker'

Vagrant.configure("2") do |config|
    config.vm.define "fastapi_app" do |fastapi_app|
        config.vm.boot_timeout = 600
        config.ssh.username = "vagrant"
        config.ssh.private_key_path = "~/.vagrant.d/insecure_private_key"
        config.ssh.insert_key = false
        #fastapi_app.vm.network "forwarded_port", guest: 443, host: 443
        fastapi_app.vm.network "forwarded_port", guest: 80, host: 9000    #, auto_correct: true
        fastapi_app.vm.provider "docker" do |fastapi_app|
            fastapi_app.build_dir = "."
            fastapi_app.name = "my_fastapi_container"
            fastapi_app.ports = ["9000:80", "127.0.0.1:2222:22"]
            fastapi_app.volumes = ["/home/ubuntu/fastapideploy:/app"]
            fastapi_app.privileged = true
            fastapi_app.create_args = ["-v", "/sys/fs/cgroup:/sys/fs/cgroup:ro"]
            fastapi_app.has_ssh = true
            fastapi_app.remains_running = true
        end
    end
end