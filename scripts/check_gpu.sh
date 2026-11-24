#!/bin/bash
# Quick GPU Check Script
# Run on Alibaba Cloud server

echo "🔍 Checking for GPU hardware..."
echo ""

# Check if any NVIDIA GPU exists
if lspci | grep -i nvidia > /dev/null; then
    echo "✅ NVIDIA GPU detected!"
    echo ""
    lspci | grep -i nvidia
    echo ""
    echo "GPU driver is NOT installed yet."
    echo ""
    echo "Next steps:"
    echo "1. Check your Alibaba Cloud instance type to confirm GPU model"
    echo "2. Install appropriate NVIDIA driver"
    echo ""
else
    echo "❌ No NVIDIA GPU found on this server!"
    echo ""
    echo "This server does NOT have a GPU."
    echo ""
    echo "Options:"
    echo "  A. Create a new GPU instance (recommended: ecs.gn6i-c4g1.xlarge with T4 GPU)"
    echo "  B. Use this server for development only (with Gemini/OpenAI API)"
    echo ""
fi

# Show instance info
echo "Instance Info:"
echo "Hostname: $(hostname)"
echo "OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
echo "Kernel: $(uname -r)"
echo "CPU: $(lscpu | grep 'Model name' | cut -d':' -f2 | xargs)"
echo "RAM: $(free -h | awk 'NR==2 {print $2}')"
echo "Disk: $(df -h / | awk 'NR==2 {print $4}' | xargs) available"
