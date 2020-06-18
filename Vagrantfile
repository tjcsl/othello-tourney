Vagrant.configure("2") do |config|

  config.vm.box = "generic/ubuntu2004"

  config.vm.network "forwarded_port", guest: 8000, host: 8000
  config.ssh.forward_agent = true
  config.vm.hostname = "othellovm"
  config.vm.boot_timeout = 600
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
  config.ssh.username = "vagrant"

end
