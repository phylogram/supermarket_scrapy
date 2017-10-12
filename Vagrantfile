# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.require_version ">= 1.8.0"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "debian-stretch"
  config.vm.box_url = "https://boxen.more-onion.com/debian-stretch.json"
  config.vm.box_version = "9.1"
  config.vm.box_download_insecure = false
  config.vm.box_check_update = false

  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "vagrant/playbook.yml"
  end

  config.vm.synced_folder ".", "/home/vagrant/hostdir"
end
