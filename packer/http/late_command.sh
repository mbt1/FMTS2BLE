apt update -y
apt upgrade -y

apt install sudo
dpkg -l sudo

apt install git -y
git config --global user.name "mbt1"
git config --global user.email "mbt1@users.noreply.github.com"
git --version

apt install bluez -y
systemctl --no-pager status bluetooth

apt install -y curl
LTS_VERSION=$(curl --silent https://nodejs.org/en/about/releases/ | grep LTS | head -1 | cut -d " " -f2)
curl -sL "https://deb.nodesource.com/setup_${LTS_VERSION}.x" | sudo -E bash -
apt install -y nodejs
node -v
