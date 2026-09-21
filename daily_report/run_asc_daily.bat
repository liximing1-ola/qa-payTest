@echo off
rem App Store 日报定时任务入口（由任务计划程序每天 10:30 调起）
rem cd 到脚本目录保证 .env / 密钥可定位；输出重定向到日志（无 console 环境下 print 安全）
cd /d "%~dp0"
"C:\Users\banban\AppData\Local\Programs\Python\Python311\python.exe" fetch_asc_daily.py >> asc_daily.log 2>&1
