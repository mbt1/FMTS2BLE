# mkdir /mnt/cdrom2;mount /dev/sr1 /mnt/cdrom2
# sh /mnt/cdrom2/late_command.sh

REPO_URL="https://github.com/mbt1/USB2FTMSBLE.git"
DEST_DIR="/home/debian/dev/USB2FTMSBLE"
BRANCH="main"


apt update -y
apt upgrade -y

apt install sudo
dpkg -l sudo
usermod -aG sudo debian

apt install git -y
git config --global user.name "mbt1"
git config --global user.email "mbt1@users.noreply.github.com"
git --version

# Create the destination directory if it doesn't exist
sudo -u debian mkdir -p "$DEST_DIR"

# Check if the repository is already cloned
if [ -d "$DEST_DIR/.git" ]; then
  echo "Repository already cloned."
else
  # Clone the repository
  sudo -u debian git clone --branch "$BRANCH" "$REPO_URL" "$DEST_DIR"
  echo "Repository cloned successfully."
fi

apt install bluez -y
systemctl --no-pager status bluetooth

apt install -y build-essential 
apt install -y curl
# LTS_VERSION=$(curl --silent https://nodejs.org/en/about/releases/ | grep LTS | head -1 | cut -d " " -f2)
# curl -sL "https://deb.nodesource.com/setup_${LTS_VERSION}.x" | sudo -E bash -
# apt install -y nodejs

sudo -u debian sh ${0%/*}/late_nonroot.sh