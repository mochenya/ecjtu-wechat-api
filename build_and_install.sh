#!/bin/bash
#
# build_and_install.sh - 构建并安装 ecjtu-wechat-api 项目包
#
# 该脚本执行以下操作：
# 1. 清理旧的构建产物
# 2. 使用 uv 构建 wheel 和 source 包
# 3. 安装包到当前 Python 环境
# 4. 验证安装是否成功
#

set -e  # 遇到错误立即退出

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 打印带颜色的信息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否在项目根目录
check_project_root() {
    if [ ! -f "pyproject.toml" ]; then
        print_error "请在项目根目录运行此脚本"
        exit 1
    fi
}

# 检查 uv 是否安装
check_uv_installed() {
    if ! command -v uv &> /dev/null; then
        print_error "未找到 uv 命令，请先安装 uv"
        print_info "安装方法: curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
    print_info "uv 版本: $(uv --version)"
}

# 清理旧的构建产物
clean_build() {
    print_info "清理旧的构建产物..."
    local folders=("dist" "build" "*.egg-info")
    for folder in "${folders[@]}"; do
        if [ -d "$folder" ] || [ -e "$folder" ]; then
            rm -rf $folder
            print_info "已删除 $folder"
        fi
    done
}

# 构建项目包
build_package() {
    local skip_tests=$1
    print_info "开始构建项目包..."

    # 运行代码检查
    print_info "运行代码检查 (ruff check)..."
    if ! uv run ruff check src; then
        print_warning "代码检查发现一些问题，请及时处理。"
    fi

    # 运行测试
    if [ "$skip_tests" = true ]; then
        print_warning "跳过测试阶段"
    else
        print_info "运行测试 (pytest)..."
        if uv run pytest; then
            print_success "所有测试通过"
        else
            print_error "测试失败，构建终止"
            exit 1
        fi
    fi

    # 构建包
    print_info "使用 uv build 构建包..."
    if uv build; then
        print_success "构建成功！"
    else
        print_error "构建失败"
        exit 1
    fi
}

# 显示构建产物
show_build_artifacts() {
    print_info "构建产物清单："
    if [ -d "dist" ]; then
        ls -lh dist/
    else
        print_error "dist/ 目录不存在"
        exit 1
    fi
}

# 安装包
install_package() {
    local install_mode=$1

    print_info "开始安装包..."

    case $install_mode in
        "global")
            print_info "安装模式: 全局 (uv pip install)"
            uv pip install dist/*.whl
            ;;
        "user")
            print_info "安装模式: 用户 (uv pip install --user)"
            uv pip install --user dist/*.whl
            ;;
        "editable")
            print_info "安装模式: 可编辑/开发 (uv pip install -e .)"
            uv pip install -e .
            ;;
        *)
            print_info "安装模式: 默认可编辑"
            uv pip install -e .
            ;;
    esac

    if [ $? -eq 0 ]; then
        print_success "安装成功！"
    else
        print_error "安装失败"
        exit 1
    fi
}

# 验证安装
verify_installation() {
    print_info "执行安装验证..."

    # 检查包是否可以导入并获取版本
    local version_info
    if version_info=$(uv run python -c "import ecjtu_wechat_api; print(ecjtu_wechat_api.__version__)" 2>/dev/null); then
        print_success "验证通过: 包 ecjtu_wechat_api (版本: $version_info) 已成功安装"
        # 显示安装路径
        local pkg_path
        pkg_path=$(uv run python -c "import ecjtu_wechat_api; print(ecjtu_wechat_api.__file__)" 2>/dev/null)
        print_info "包位置: $pkg_path"
    else
        print_error "验证失败: 无法导入 ecjtu_wechat_api 包"
        exit 1
    fi
}

# 显示使用帮助
show_usage() {
    cat << EOF
用法: $0 [选项]

选项:
  -g, --global      全局安装
  -u, --user        用户级安装
  -e, --editable    可编辑安装 (开发模式，默认)
  -b, --build-only  仅构建，不安装
  -c, --clean       仅清理构建产物
  -s, --skip-tests  构建时跳过测试 (不推荐)
  -h, --help        显示此帮助信息

示例:
  $0                 # 默认：构建并可编辑安装
  $0 --build-only    # 仅构建并运行测试
  $0 -b -s           # 仅构建且跳过测试
  $0 --clean         # 仅清理
EOF
}

# 主函数
main() {
    local install_mode="editable"
    local build_only=false
    local clean_only=false
    local skip_tests=false

    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -g|--global)     install_mode="global"; shift ;;
            -u|--user)       install_mode="user"; shift ;;
            -e|--editable)   install_mode="editable"; shift ;;
            -b|--build-only) build_only=true; shift ;;
            -c|--clean)      clean_only=true; shift ;;
            -s|--skip-tests) skip_tests=true; shift ;;
            -h|--help)       show_usage; exit 0 ;;
            *)               print_error "未知选项: $1"; show_usage; exit 1 ;;
        esac
    done

    # 仅清理模式
    if [ "$clean_only" = true ]; then
        clean_build
        print_success "清理完成"
        exit 0
    fi

    echo "=========================================="
    echo "   ECJTU WeChat API Build & Install"
    echo "=========================================="

    check_project_root
    check_uv_installed

    clean_build
    build_package "$skip_tests"
    show_build_artifacts

    if [ "$build_only" = true ]; then
        print_success "构建流程完成 (未执行安装)"
        exit 0
    fi

    install_package "$install_mode"
    verify_installation

    echo "=========================================="
    print_success "所有流程顺利完成！"
    echo "=========================================="
    echo ""
    echo "快速启动:"
    echo "  uv run uvicorn ecjtu_wechat_api.main:app --reload --port 6894"
    echo ""
}

main "$@"