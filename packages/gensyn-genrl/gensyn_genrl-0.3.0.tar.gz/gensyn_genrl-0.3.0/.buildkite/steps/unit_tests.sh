set -exu
source ~/.profile

# Install and verify Deno exists on PATH
sudo apt-get install unzip -y
curl -fsSL https://deno.land/install.sh | sh
export DENO_INSTALL="$HOME/.deno"
export PATH="$DENO_INSTALL/bin:$PATH"

deno --version

pip install .[dev]
pip install .[examples]
pytest test
