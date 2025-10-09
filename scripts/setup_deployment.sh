#!/bin/bash
# Setup script for deployment user on server
# Run this script on your server to prepare it for GitHub Actions deployment

set -e  # Exit on error

echo "========================================="
echo "🚀 MechBook Deployment Setup"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Please run as root (use sudo)${NC}"
    exit 1
fi

# Configuration
DEPLOY_USER="deploy"
PROJECT_NAME="MechBook"
PROJECT_PATH="/home/$DEPLOY_USER/apps/$PROJECT_NAME"
GITHUB_REPO="https://github.com/YOUR_USERNAME/MechBook.git"  # CHANGE THIS!

echo ""
echo "Configuration:"
echo "- Deploy user: $DEPLOY_USER"
echo "- Project path: $PROJECT_PATH"
echo "- GitHub repo: $GITHUB_REPO"
echo ""

read -p "Is this correct? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Please edit this script and update GITHUB_REPO variable"
    exit 1
fi

# Step 1: Create deploy user
echo ""
echo "========================================="
echo "Step 1: Creating deploy user..."
echo "========================================="

if id "$DEPLOY_USER" &>/dev/null; then
    echo -e "${YELLOW}⚠️  User $DEPLOY_USER already exists${NC}"
else
    adduser --disabled-password --gecos "" $DEPLOY_USER
    echo -e "${GREEN}✅ User $DEPLOY_USER created${NC}"
fi

# Step 2: Add user to docker group
echo ""
echo "========================================="
echo "Step 2: Adding user to docker group..."
echo "========================================="

usermod -aG docker $DEPLOY_USER
echo -e "${GREEN}✅ User added to docker group${NC}"

# Step 3: Setup SSH
echo ""
echo "========================================="
echo "Step 3: Setting up SSH keys..."
echo "========================================="

sudo -u $DEPLOY_USER bash << 'EOF'
cd ~
mkdir -p .ssh
chmod 700 .ssh

# Generate SSH key for GitHub Actions
if [ ! -f .ssh/github_actions ]; then
    ssh-keygen -t ed25519 -C "github-actions-deploy" -f .ssh/github_actions -N ""
    echo "✅ SSH key generated"
else
    echo "⚠️  SSH key already exists"
fi

# Add public key to authorized_keys
cat .ssh/github_actions.pub >> .ssh/authorized_keys
chmod 600 .ssh/authorized_keys

echo ""
echo "========================================="
echo "📋 IMPORTANT: Copy this private key to GitHub Secrets"
echo "========================================="
echo ""
cat .ssh/github_actions
echo ""
echo "========================================="
echo "GitHub Settings → Secrets → New secret"
echo "Name: SSH_PRIVATE_KEY"
echo "Value: (paste the entire key above)"
echo "========================================="
echo ""
EOF

# Step 4: Setup project directory
echo ""
echo "========================================="
echo "Step 4: Setting up project directory..."
echo "========================================="

sudo -u $DEPLOY_USER bash -c "mkdir -p /home/$DEPLOY_USER/apps"

# Clone repository if not exists
if [ -d "$PROJECT_PATH" ]; then
    echo -e "${YELLOW}⚠️  Project directory already exists${NC}"
    echo "Path: $PROJECT_PATH"
else
    echo "Cloning repository..."
    sudo -u $DEPLOY_USER git clone $GITHUB_REPO $PROJECT_PATH
    echo -e "${GREEN}✅ Repository cloned${NC}"
fi

# Step 5: Create environment files
echo ""
echo "========================================="
echo "Step 5: Creating environment files..."
echo "========================================="

cd $PROJECT_PATH

# Create .env.db if not exists
if [ ! -f .env.db ]; then
    cat > .env.db << 'ENVEOF'
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=mechbook_db
ENVEOF
    chown $DEPLOY_USER:$DEPLOY_USER .env.db
    chmod 600 .env.db
    echo -e "${YELLOW}⚠️  Created .env.db - PLEASE EDIT IT!${NC}"
else
    echo -e "${GREEN}✅ .env.db already exists${NC}"
fi

# Create backend/.env if not exists
if [ ! -f backend/.env ]; then
    mkdir -p backend
    cat > backend/.env << 'ENVEOF'
SECRET_KEY=your_secret_key_here_change_this
DATABASE_URL=postgresql://your_db_user:your_secure_password@db:5432/mechbook_db
ELASTICSEARCH_HOST=es:9200
ENVEOF
    chown $DEPLOY_USER:$DEPLOY_USER backend/.env
    chmod 600 backend/.env
    echo -e "${YELLOW}⚠️  Created backend/.env - PLEASE EDIT IT!${NC}"
else
    echo -e "${GREEN}✅ backend/.env already exists${NC}"
fi

# Step 6: Test docker-compose
echo ""
echo "========================================="
echo "Step 6: Testing docker-compose..."
echo "========================================="

cd $PROJECT_PATH
if sudo -u $DEPLOY_USER docker-compose config > /dev/null 2>&1; then
    echo -e "${GREEN}✅ docker-compose config is valid${NC}"
else
    echo -e "${RED}❌ docker-compose config has errors${NC}"
    sudo -u $DEPLOY_USER docker-compose config
    exit 1
fi

# Step 7: Setup firewall (if UFW is installed)
echo ""
echo "========================================="
echo "Step 7: Checking firewall..."
echo "========================================="

if command -v ufw &> /dev/null; then
    echo "Ensuring required ports are open..."
    ufw allow 22/tcp   # SSH
    ufw allow 80/tcp   # HTTP
    ufw allow 443/tcp  # HTTPS
    echo -e "${GREEN}✅ Firewall configured${NC}"
else
    echo -e "${YELLOW}⚠️  UFW not installed, skipping firewall setup${NC}"
fi

# Final summary
echo ""
echo "========================================="
echo "✅ Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. ⚠️  EDIT the .env files with real credentials:"
echo "   - $PROJECT_PATH/.env.db"
echo "   - $PROJECT_PATH/backend/.env"
echo ""
echo "2. 📋 Add GitHub Secrets (see private key above):"
echo "   - SSH_PRIVATE_KEY"
echo "   - SSH_HOST (your server IP or hostname)"
echo "   - SSH_USER ($DEPLOY_USER)"
echo "   - SSH_PORT (usually 22)"
echo ""
echo "3. 🚀 Push code to GitHub:"
echo "   git push origin master"
echo ""
echo "4. 📊 Monitor deployment:"
echo "   https://github.com/YOUR_USERNAME/MechBook/actions"
echo ""
echo "========================================="


