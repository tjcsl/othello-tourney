Vagrant.configure("2") do |config|

  config.vm.box = "ubuntu/bionic64"

  config.vm.network "forwarded_port", guest: 8000, host: 8000
  config.ssh.forward_agent = true
  config.vm.hostname = "othellovm"
  config.vm.define "othello-vagrant" do |v|
  end

  config.vm.provider :virtualbox do |vb|
    vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    vb.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
    vb.customize ["modifyvm", :id, "--nictype1", "virtio"]
    vb.name = "othello-vagrant"
    vb.memory = 2048 # the default of 512 gives us a OOM during setup.
  end
  config.vm.network :private_network, ip: '192.168.50.50'

  config.vm.synced_folder ".", "/home/vagrant/othello"

  config.vm.provision "shell", path: "config/vagrant/provision_vagrant.sh"
  config.vm.provision "shell", path: "config/vagrant/install_pyenv.sh", privileged: false
  config.vm.provision "shell", path: "config/vagrant/setup_project.sh", privileged: false
  config.ssh.username = "vagrant"

end
