# 隧道围岩变形预测与支护设计辅助软件

本项目是围绕“隧道围岩变形预测与支护设计辅助”主题从零生成的独立 Web 系统，采用 Python 标准库后端、原生前端和本地 JSON 数据仓。目标不是做泛化工程平台，而是把区段台账、监测趋势、情景预测、支护复核和交付校核收束到一个控制台里。

## 启动方式

```bash
python -X utf8 scripts/seed_demo_data.py
python apps/api/main.py
```

浏览器访问：

```text
http://127.0.0.1:8010
```

## 演示账号

- `admin / admin123`
- `monitor / admin123`
- `support / admin123`

## 自动化命令

```bash
python -X utf8 scripts/run_tests.py
python -X utf8 scripts/ai_slop_check_placeholder.py --project-dir .
python -X utf8 scripts/build_materials.py --name "隧道围岩变形预测与支护设计辅助软件" --output-dir .
```

