#!/bin/bash

echo "🔧 Fixing Node.js Version Issue..."
echo "Current Node.js version: $(node --version)"
echo "Required: >=20.9.0"
echo ""

# Check if nvm is installed
if [ -s "$HOME/.nvm/nvm.sh" ] || [ -s "$HOME/.nvm/nvm.sh" ]; then
    echo "✅ Found nvm, using it to install Node.js 20..."
    if [ -s "$HOME/.nvm/nvm.sh" ]; then
        source "$HOME/.nvm/nvm.sh"
    else
        export NVM_DIR="$HOME/.nvm"
        [ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"
    fi
    nvm install 20
    nvm use 20
    nvm alias default 20
    echo ""
    echo "✅ Node.js version updated!"
    node --version
    echo ""
    echo "Now run: ./restart.sh"
elif command -v brew &> /dev/null; then
    if brew list node@20 &> /dev/null; then
        echo "✅ Node.js 20 is already installed via Homebrew!"
        echo ""
        echo "Adding to PATH for this session..."
        if [ -d "/opt/homebrew/opt/node@20" ]; then
            export PATH="/opt/homebrew/opt/node@20/bin:$PATH"
        elif [ -d "/usr/local/opt/node@20" ]; then
            export PATH="/usr/local/opt/node@20/bin:$PATH"
        fi
        
        echo ""
        echo "New Node.js version: $(node --version)"
        echo ""
        echo "⚠️  To make this permanent, add this to your ~/.zshrc:"
        if [ -d "/opt/homebrew/opt/node@20" ]; then
            echo "   export PATH=\"/opt/homebrew/opt/node@20/bin:\$PATH\""
            echo ""
            echo "Or run: echo 'export PATH=\"/opt/homebrew/opt/node@20/bin:\$PATH\"' >> ~/.zshrc"
        else
            echo "   export PATH=\"/usr/local/opt/node@20/bin:\$PATH\""
            echo ""
            echo "Or run: echo 'export PATH=\"/usr/local/opt/node@20/bin:\$PATH\"' >> ~/.zshrc"
        fi
        echo ""
        echo "For now, you can run: ./restart.sh"
    else
        echo "📦 Installing Node.js 20 via Homebrew..."
        echo "This may take a few minutes..."
        brew install node@20
        
        echo ""
        echo "✅ Node.js 20 installed!"
        echo ""
        echo "Adding to PATH for this session..."
        if [ -d "/opt/homebrew/opt/node@20" ]; then
            export PATH="/opt/homebrew/opt/node@20/bin:$PATH"
        elif [ -d "/usr/local/opt/node@20" ]; then
            export PATH="/usr/local/opt/node@20/bin:$PATH"
        fi
        
        echo ""
        echo "New Node.js version: $(node --version)"
        echo ""
        echo "⚠️  To make this permanent, add this to your ~/.zshrc:"
        if [ -d "/opt/homebrew/opt/node@20" ]; then
            echo "   export PATH=\"/opt/homebrew/opt/node@20/bin:\$PATH\""
            echo ""
            echo "Or run: echo 'export PATH=\"/opt/homebrew/opt/node@20/bin:\$PATH\"' >> ~/.zshrc"
        else
            echo "   export PATH=\"/usr/local/opt/node@20/bin:\$PATH\""
            echo ""
            echo "Or run: echo 'export PATH=\"/usr/local/opt/node@20/bin:\$PATH\"' >> ~/.zshrc"
        fi
        echo ""
        echo "For now, you can run: ./restart.sh"
    fi
else
    echo "❌ Neither nvm nor Homebrew found."
    echo ""
    echo "Please install Node.js 20+ manually:"
    echo "1. Install nvm:"
    echo "   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash"
    echo "   Then restart terminal and run: nvm install 20 && nvm use 20"
    echo ""
    echo "2. Or download from: https://nodejs.org/"
    echo "   (Download the LTS version 20.x or higher)"
    echo ""
    echo "3. After installing, run: ./restart.sh"
fi

