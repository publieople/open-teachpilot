#!/bin/bash
#
# TeachPilot 生产环境部署脚本
# 服务外包大赛 A04 题目 - 多模态 AI 互动式教学智能体
#
# 使用方法：
#   ./deploy/deploy.sh [dev|prod]
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查环境
check_environment() {
    log_info "检查运行环境..."
    
    # 检查 Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    # 检查 Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    # 检查 .env 文件
    if [ ! -f ".env" ]; then
        log_warn ".env 文件不存在，从 .env.teachpilot 复制模板"
        cp .env.teachpilot .env
        log_warn "请编辑 .env 文件配置必要的环境变量"
        exit 1
    fi
    
    log_info "环境检查通过"
}

# 生成安全密钥
generate_secret_key() {
    if [ -z "$WEBUI_SECRET_KEY" ] || [ "$WEBUI_SECRET_KEY" = "teachpilot-secret-key-change-in-production" ]; then
        log_info "生成安全密钥..."
        SECRET_KEY=$(openssl rand -hex 32)
        sed -i "s/WEBUI_SECRET_KEY=.*/WEBUI_SECRET_KEY=$SECRET_KEY/" .env
        log_info "安全密钥已生成并保存到 .env"
    fi
}

# 部署开发环境
deploy_dev() {
    log_info "部署开发环境..."
    
    docker-compose -f docker-compose.teachpilot.yaml down --remove-orphans 2>/dev/null || true
    docker-compose -f docker-compose.teachpilot.yaml up -d --build
    
    log_info "开发环境部署完成"
    log_info "访问地址：http://localhost:3000"
}

# 部署生产环境
deploy_prod() {
    log_info "部署生产环境..."
    
    # 检查必要的环境变量
    if [ -z "$OPENROUTER_API_KEY" ]; then
        log_error "OPENROUTER_API_KEY 未配置"
        exit 1
    fi
    
    # 生成安全密钥
    generate_secret_key
    
    # 创建必要的目录
    mkdir -p nginx/ssl
    mkdir -p logs
    
    # 停止旧服务
    docker-compose -f docker-compose.teachpilot.prod.yaml down --remove-orphans 2>/dev/null || true
    
    # 启动服务
    docker-compose -f docker-compose.teachpilot.prod.yaml up -d --build
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 30
    
    # 健康检查
    if docker-compose -f docker-compose.teachpilot.prod.yaml ps | grep -q "teachpilot-app.*Up"; then
        log_info "TeachPilot 应用启动成功"
    else
        log_error "TeachPilot 应用启动失败，请检查日志"
        docker-compose -f docker-compose.teachpilot.prod.yaml logs teachpilot
        exit 1
    fi
    
    log_info "生产环境部署完成"
    log_info "访问地址：http://localhost:3000"
}

# 查看日志
view_logs() {
    local service=$1
    if [ -n "$service" ]; then
        docker-compose -f docker-compose.teachpilot.prod.yaml logs -f $service
    else
        docker-compose -f docker-compose.teachpilot.prod.yaml logs -f
    fi
}

# 备份数据
backup_data() {
    log_info "备份数据..."
    
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p $BACKUP_DIR
    
    # 备份 PostgreSQL 数据
    docker exec teachpilot-postgres pg_dump -U teachpilot teachpilot > $BACKUP_DIR/postgres.sql
    
    # 备份应用数据
    docker cp teachpilot-app:/app/backend/data $BACKUP_DIR/app-data
    
    log_info "数据备份完成：$BACKUP_DIR"
}

# 恢复数据
restore_data() {
    local backup_dir=$1
    if [ -z "$backup_dir" ]; then
        log_error "请指定备份目录"
        exit 1
    fi
    
    log_info "从 $backup_dir 恢复数据..."
    
    # 恢复 PostgreSQL 数据
    cat $backup_dir/postgres.sql | docker exec -i teachpilot-postgres psql -U teachpilot -d teachpilot
    
    # 恢复应用数据
    docker cp $backup_dir/app-data teachpilot-app:/app/backend
    
    log_info "数据恢复完成"
}

# 显示帮助
show_help() {
    echo "TeachPilot 部署脚本"
    echo ""
    echo "使用方法：$0 [命令] [选项]"
    echo ""
    echo "命令:"
    echo "  dev         部署开发环境"
    echo "  prod        部署生产环境"
    echo "  logs        查看日志 [服务名]"
    echo "  backup      备份数据"
    echo "  restore     恢复数据 <备份目录>"
    echo "  status      查看服务状态"
    echo "  help        显示帮助"
    echo ""
}

# 主函数
main() {
    local command=$1
    shift || true
    
    case $command in
        dev)
            check_environment
            deploy_dev
            ;;
        prod)
            check_environment
            deploy_prod
            ;;
        logs)
            view_logs "$@"
            ;;
        backup)
            backup_data
            ;;
        restore)
            restore_data "$@"
            ;;
        status)
            docker-compose -f docker-compose.teachpilot.prod.yaml ps
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知命令：$command"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
