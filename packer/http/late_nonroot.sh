git config --global user.name "mbt1"
git config --global user.email "mbt1@users.noreply.github.com"

curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.38.0/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
command -v nvm
nvm --version
nvm install --lts
node -v
npm -v
npm install -g npm
npm install -g express
npm install
