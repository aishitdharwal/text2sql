#!/bin/bash

# Install/upgrade LangFuse
echo "Installing LangFuse..."
pip install --upgrade langfuse

# Verify installation
echo ""
echo "Verifying installation..."
python3 -c "from langfuse import Langfuse; print('✅ LangFuse installed successfully')" 2>/dev/null

if [ $? -eq 0 ]; then
    echo ""
    echo "Testing decorators..."
    python3 -c "from langfuse.decorators import observe, langfuse_context; print('✅ Decorators available')" 2>/dev/null
    
    if [ $? -ne 0 ]; then
        echo "⚠️  Decorators not found - trying alternative import..."
        python3 -c "from langfuse import Langfuse; print('✅ Base module works - decorators will use fallback')"
    fi
else
    echo "❌ Failed to install LangFuse"
    exit 1
fi

echo ""
echo "LangFuse setup complete!"
echo ""
echo "Next steps:"
echo "1. Sign up at: https://cloud.langfuse.com"
echo "2. Get your API keys from: Settings → API Keys"
echo "3. Add to .env:"
echo "   ENABLE_LANGFUSE=true"
echo "   LANGFUSE_PUBLIC_KEY=pk-lf-..."
echo "   LANGFUSE_SECRET_KEY=sk-lf-..."
echo "4. Restart backend: ./run.sh"
