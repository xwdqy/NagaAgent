#!/bin/bash
# 一键配置脚本 for NagaAgent 3.0 (Mac 版本)
# 版本号由config.py统一管理

set -e  # 设置错误时停止执行

PYTHON_MIN_VERSION="3.10"  # Python最低版本要求
VENV_PATH=".venv"  # 虚拟环境路径

# 颜色输出函数
print_info() {
    echo -e "\033[34m[INFO]\033[0m $1"
}

print_success() {
    echo -e "\033[32m[SUCCESS]\033[0m $1"
}

print_error() {
    echo -e "\033[31m[ERROR]\033[0m $1"
}

print_warning() {
    echo -e "\033[33m[WARNING]\033[0m $1"
}

# 检查 Python 版本
print_info "检查 Python 版本..."
if ! command -v python3 &> /dev/null; then
    print_error "未找到 python3 命令，请先安装 Python 3.10+"
    print_info "推荐使用 Homebrew 安装: brew install python@3.11"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | grep -o '[0-9]\+\.[0-9]\+')
REQUIRED_VERSION="3.10"

if [[ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]]; then
    print_error "需要 Python $PYTHON_MIN_VERSION 或更高版本，当前版本: $PYTHON_VERSION"
    exit 1
fi

print_success "Python 版本检查通过: $PYTHON_VERSION"

# 设置工作目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 创建并激活虚拟环境
if [[ ! -d "$VENV_PATH" ]]; then
    print_info "创建虚拟环境..."
    python3 -m venv "$VENV_PATH"
fi

print_info "激活虚拟环境..."
source "$VENV_PATH/bin/activate"

# 升级 pip
print_info "升级 pip..."
pip install --upgrade pip

# 检查是否为 Apple Silicon Mac
if [[ $(uname -m) == "arm64" ]]; then
    print_info "检测到 Apple Silicon Mac，将安装适配的依赖..."
    # 对于 Apple Silicon，某些包可能需要特殊处理
    export SYSTEM_VERSION_COMPAT=1
fi

# 安装系统依赖 (macOS 特定)
print_info "检查系统依赖..."
if ! command -v portaudio &> /dev/null; then
    print_warning "未检测到 PortAudio，PyAudio 可能安装失败"
    print_info "如需语音功能，请运行: brew install portaudio"
fi

# 安装核心依赖 (需要编译的包)
print_info "安装核心依赖 (numpy, pandas, scipy)..."
if pip install --only-binary=all numpy pandas scipy; then
    print_success "核心依赖安装成功"
else
    print_warning "使用 --only-binary 安装失败，尝试普通安装..."
    if pip install numpy pandas scipy; then
        print_success "核心依赖安装成功"
    else
        print_error "核心依赖安装失败，请检查编译环境"
        exit 1
    fi
fi

# 安装基础依赖
print_info "安装基础依赖..."
basic_deps=("mcp" "openai" "openai-agents" "python-dotenv" "requests" "aiohttp" "pytz" "colorama" "python-dateutil")
for dep in "${basic_deps[@]}"; do
    if pip install "$dep"; then
        print_success "已安装 $dep"
    else
        print_warning "安装 $dep 失败"
    fi
done

# 安装 GRAG 知识图谱依赖
print_info "安装 GRAG 知识图谱依赖..."
grag_deps=("py2neo" "pyvis" "matplotlib")
for dep in "${grag_deps[@]}"; do
    if pip install "$dep"; then
        print_success "已安装 $dep"
    else
        print_warning "安装 $dep 失败"
    fi
done

# 安装 API 服务器依赖
print_info "安装 API 服务器依赖..."
api_deps=("flask-cors" "flask" "gevent" "edge-tts" "emoji" "fastapi")
for dep in "${api_deps[@]}"; do
    if pip install "$dep"; then
        print_success "已安装 $dep"
    else
        print_warning "安装 $dep 失败"
    fi
done

# 安装网络通信依赖
print_info "安装网络通信依赖..."
network_deps=("uvicorn" "librosa" "websockets")
for dep in "${network_deps[@]}"; do
    if pip install "$dep"; then
        print_success "已安装 $dep"
    else
        print_warning "安装 $dep 失败"
    fi
done

# 安装 AI/ML 依赖
print_info "安装 AI/ML 依赖..."
ai_deps=("tqdm" "scikit-learn" "transformers")
for dep in "${ai_deps[@]}"; do
    if pip install "$dep"; then
        print_success "已安装 $dep"
    else
        print_warning "安装 $dep 失败"
    fi
done

# 安装数据处理依赖
print_info "安装数据处理依赖..."
data_deps=("pydantic" "pydantic-settings" "griffe" "anyio" "httpx" "httpx-sse" "sse-starlette" "starlette" "certifi" "charset-normalizer" "idna" "urllib3" "typing-extensions" "markdown")
for dep in "${data_deps[@]}"; do
    if pip install "$dep"; then
        print_success "已安装 $dep"
    else
        print_warning "安装 $dep 失败"
    fi
done

# 安装 GUI 依赖
print_info "安装 GUI 依赖..."
gui_deps=("playwright" "greenlet" "pyee" "pygame" "html2text")
for dep in "${gui_deps[@]}"; do
    if pip install "$dep"; then
        print_success "已安装 $dep"
    else
        print_warning "安装 $dep 失败"
    fi
done

# 安装音频处理依赖
print_info "安装音频处理依赖..."
audio_deps=("sounddevice" "soundfile" "pyaudio" "edge-tts" "emoji")
for dep in "${audio_deps[@]}"; do
    if pip install "$dep"; then
        print_success "已安装 $dep"
    else
        print_warning "安装 $dep 失败"
    fi
done

# 安装 PyQt5
print_info "安装 PyQt5..."
if pip install pyqt5; then
    print_success "PyQt5 安装成功"
else
    print_warning "PyQt5 安装失败"
fi

# 安装系统托盘依赖
print_info "安装系统托盘依赖..."
tray_deps=("pystray" "pillow")
for dep in "${tray_deps[@]}"; do
    if pip install "$dep"; then
        print_success "已安装 $dep"
    else
        print_warning "安装 $dep 失败"
    fi
done

# 安装其他工具依赖
print_info "安装其他工具依赖..."
tool_deps=("tiktoken" "bottleneck")
for dep in "${tool_deps[@]}"; do
    if pip install "$dep"; then
        print_success "已安装 $dep"
    else
        print_warning "安装 $dep 失败"
    fi
done

# 特殊处理可能在 Mac 上有问题的包
print_info "检查特殊依赖..."

# PyAudio 在 Mac 上可能需要特殊处理
if ! pip show pyaudio > /dev/null 2>&1; then
    print_warning "PyAudio 安装失败，尝试使用 Homebrew 方式..."
    if command -v brew &> /dev/null; then
        brew install portaudio
        pip install pyaudio
    else
        print_warning "未找到 Homebrew，请手动安装 PortAudio: https://formulae.brew.sh/formula/portaudio"
    fi
fi

# 安装 playwright 浏览器驱动
print_info "安装 playwright 浏览器驱动..."
if python -m playwright install chromium; then
    print_success "Playwright Chromium 安装成功"
else
    print_warning "Playwright 浏览器驱动安装失败"
fi

# 验证关键依赖
print_info "验证关键依赖..."
critical_deps=("numpy" "pandas" "pyqt5" "pystray" "pillow")
for dep in "${critical_deps[@]}"; do
    if python -c "import $dep; print('$dep - OK')" 2>/dev/null; then
        print_success "$dep 验证通过"
    else
        print_warning "$dep 验证失败"
    fi
done

# 验证 playwright 安装
print_info "验证 playwright 安装..."
if PLAYWRIGHT_VERSION=$(python -m playwright --version 2>/dev/null); then
    print_success "Playwright 版本: $PLAYWRIGHT_VERSION"
else
    print_warning "Playwright 安装验证失败"
fi

# 测试托盘功能
print_info "测试托盘功能..."
if python -c "import pystray, PIL; print('Tray dependencies - OK')" 2>/dev/null; then
    print_success "托盘功能测试通过"
else
    print_warning "托盘功能测试失败"
fi

# 创建启动脚本
print_info "创建启动脚本..."
cat > start_mac.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source .venv/bin/activate
export PYTHONPATH="$(pwd):$PYTHONPATH"
python main.py
EOF

chmod +x start_mac.sh

print_success "环境设置完成！"
print_info "启动方式:"
print_info "  ./start_mac.sh"
print_info ""
print_info "托盘模式启动:"
print_info "  pythonw main.py"
print_info ""
print_info "如需安装其他浏览器驱动，请运行:"
print_info "  python -m playwright install firefox   # 安装 Firefox"
print_info "  python -m playwright install webkit    # 安装 WebKit"
print_info ""
print_info "如遇到权限问题，请运行: chmod +x setup_mac.sh start_mac.sh" 