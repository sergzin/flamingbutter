require "vagrant-host-shell"


Vagrant.configure(2) do |config|


  config.vm.define "neo4j", primary: true do |linux|
    linux.vm.box = "debian/jessie64"
    linux.vm.box_version = "8.2.0"
    linux.vm.hostname = "Linux"
    linux.ssh.shell = "bash -c 'BASH_ENV=/etc/profile exec bash'"
    linux.vm.network :forwarded_port, guest: 7474, host: 7474

    linux.vm.provision :shell, keep_color: true do |sh|
      sh.path = "provisioning/provision.sh"
      sh.args = "provisioning/setup.yml provisioning/hosts"
    end
    linux.vm.provider "virtualbox" do |vb|
      vb.check_guest_additions = false
	  vb.memory = 2048
	  vb.cpus = 2
    end
  end

end