@echo off
setlocal

:: 设置日志文件路径
set LOG_FILE=%~dp0celery_startup.log

echo ==================== 启动时间: %date% %time% ==================== > "%LOG_FILE%"
echo 正在诊断 Celery 启动环境... >> "%LOG_FILE%"

:: === 步骤1: 进入D盘 ===
echo [步骤1] 进入D盘... >> "%LOG_FILE%"
d: 2>> "%LOG_FILE%"
if errorlevel 1 (
    echo [错误] 无法进入D盘 >> "%LOG_FILE%"
    goto :error
)

:: === 步骤2: 激活虚拟环境 ===
echo [步骤2] 激活虚拟环境... >> "%LOG_FILE%"
call d:\Python\py_env\mainmgmt_vue_new\Scripts\activate.bat 2>> "%LOG_FILE%"
if errorlevel 1 (
    echo [错误] 虚拟环境激活失败 >> "%LOG_FILE%"
    goto :error
)

:: 验证虚拟环境
echo [验证] 当前Python: >> "%LOG_FILE%"
where python >> "%LOG_FILE%" 2>&1

:: === 步骤3: 进入项目目录 ===
echo [步骤3] 进入项目目录... >> "%LOG_FILE%"
cd d:\Python\django5\mainmgmt_drf_vue_new\MainMgmt_back 2>> "%LOG_FILE%"
if errorlevel 1 (
    echo [错误] 项目目录不存在 >> "%LOG_FILE%"
    goto :error
)

:: 验证目录
echo [验证] 当前目录: >> "%LOG_FILE%"
cd >> "%LOG_FILE%"
echo [验证] manage.py 存在: >> "%LOG_FILE%"
dir manage.py >> "%LOG_FILE%" 2>&1

:: === 步骤4: 验证 Celery 安装 ===
echo [步骤4] 验证 Celery 安装... >> "%LOG_FILE%"
where celery.exe >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo [错误] Celery 未在虚拟环境中安装 >> "%LOG_FILE%"
    goto :error
)

:: === 步骤5: 测试 Redis 连接 ===
echo [步骤5] 测试 Redis 连接... >> "%LOG_FILE%"
python -c "import redis; r = redis.Redis(); print('Redis Ping:', r.ping())" >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo [警告] Redis 连接失败 >> "%LOG_FILE%"
    echo 请确保 Redis 服务已启动: redis-server >> "%LOG_FILE%"
    echo 或检查 .env 中的 Redis 地址配置 >> "%LOG_FILE%"
    goto :error
)

:: === 步骤6: 测试 Django 配置 ===
echo [步骤6] 测试 Django 配置... >> "%LOG_FILE%"
python -c "import django; django.setup(); from django.conf import settings; print('Celery Broker:', settings.CELERY_BROKER_URL)" >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo [错误] Django 配置加载失败 >> "%LOG_FILE%"
    goto :error
)

:: === 步骤7: 启动 Celery Worker ===
echo [步骤7] 正在启动 Celery Worker... >> "%LOG_FILE%"
echo 启动命令: python -m celery -A mainmgmt worker -l info --pool=solo >> "%LOG_FILE%"
echo 请等待... >> "%LOG_FILE%"

:: 尝试启动并捕获错误
python -m celery -A mainmgmt worker -l info --pool=solo 2>&1 | findstr /V "mingle" > "%LOG_FILE%_temp.txt"
type "%LOG_FILE%_temp.txt" >> "%LOG_FILE%"

:: 检查是否包含错误关键字
findstr /i "error\|exception\|traceback" "%LOG_FILE%_temp.txt" >nul
if errorlevel 1 (
    echo [成功] Celery 启动成功！ >> "%LOG_FILE%"
    echo 日志保存在: %LOG_FILE%
    echo.
    echo Celery 已正常启动，请保持此窗口运行...
    pause
    exit /b 0
) else (
    echo [错误] Celery 启动过程中出现错误 >> "%LOG_FILE%"
    goto :error
)

:error
echo.
echo ==================== 启动失败 ====================
echo 错误详细信息已保存到: %LOG_FILE%
echo.
echo 最后 20 行错误日志:
echo --------------------------------------------------
type "%LOG_FILE%" | findstr /