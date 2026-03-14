# GroupManager 插件开发文档

## 项目结构

```
GroupManager/
├── groupmanager/              # 插件主包
│   ├── __init__.py           # 包初始化
│   ├── core/                 # 核心模块
│   │   ├── __init__.py
│   │   ├── config.py         # 配置管理
│   │   ├── storage.py        # 数据存储
│   │   └── validator.py      # 验证器
│   ├── handlers/             # 处理器模块
│   │   ├── __init__.py
│   │   ├── rule_handler.py           # 规则处理器
│   │   └── whitelist_blacklist_handler.py  # 白名单/黑名单处理器
│   └── utils/                # 工具模块
│       ├── __init__.py
│       ├── message_builder.py        # 消息构建器
│       └── permission.py             # 权限检查
├── tests/                    # 测试模块
│   ├── __init__.py
│   └── test_core.py          # 核心模块测试
├── main.py                   # 插件入口
├── metadata.yaml             # 插件元数据
├── _conf_schema.json         # 配置模式
├── requirements.txt          # 依赖列表
├── ruff.toml                 # Ruff 配置
├── README.md                 # 项目文档
├── CHANGELOG.md              # 更新日志
└── LICENSE                   # 许可证
```

## 模块说明

### 核心模块 (core/)

#### config.py
配置管理类，负责：
- 管理管理员列表
- 管理默认模式
- 管理日志设置
- 检查用户权限

#### storage.py
数据存储类，负责：
- 使用 AstrBot KV 存储接口
- 存储和读取规则数据
- 存储和读取白名单数据
- 存储和读取黑名单数据
- 提供便捷的添加/删除方法

#### validator.py
验证器类，负责：
- 判断是否为正则表达式
- 验证正则表达式有效性
- 测试模式匹配
- 验证加群申请

### 处理器模块 (handlers/)

#### rule_handler.py
规则处理器，负责：
- 添加规则
- 删除规则
- 查看规则列表
- 清空规则
- 测试规则匹配

#### whitelist_blacklist_handler.py
白名单/黑名单处理器，负责：
- 添加用户到白名单
- 从白名单移除用户
- 查看白名单
- 添加用户到黑名单
- 从黑名单移除用户
- 查看黑名单

### 工具模块 (utils/)

#### message_builder.py
消息构建器，负责：
- 构建各种类型的消息
- 格式化规则列表
- 格式化白名单/黑名单
- 构建测试结果
- 构建帮助消息

#### permission.py
权限检查模块，负责：
- 检查用户是否为管理员

## 开发规范

### 代码风格
- 遵循 PEP 8 代码风格
- 使用类型注解
- 编写详细的文档字符串
- 使用有意义的变量名和函数名

### 错误处理
- 使用 try-except 捕获异常
- 提供清晰的错误信息
- 不要让插件因一个错误而崩溃

### 数据存储
- 使用 AstrBot 提供的 KV 存储接口
- 数据存储在 data 目录下
- 避免在插件目录存储持久化数据

### 测试
- 编写单元测试
- 测试核心功能
- 测试边界情况

## 部署流程

1. 使用 ruff 格式化代码：
```bash
ruff format .
ruff check .
```

2. 运行测试：
```bash
pytest tests/
```

3. 检查代码错误：
使用 AstrBot 的错误检查功能

4. 更新文档：
- 更新 README.md
- 更新 CHANGELOG.md

5. 提交代码：
```bash
git add .
git commit -m "更新内容"
git push
```

## 扩展指南

### 添加新的验证方式

1. 在 `validator.py` 中添加新的验证逻辑
2. 在 `storage.py` 中添加存储方法（如果需要）
3. 在 `rule_handler.py` 中添加处理方法
4. 更新配置模式（如果需要）

### 添加新的指令

1. 在对应的处理器中添加新方法
2. 使用 `@gm.command()` 或 `@gm.group()` 装饰器
3. 实现业务逻辑
4. 更新帮助消息

### 自定义消息样式

1. 在 `message_builder.py` 中添加新的构建方法
2. 使用 emoji 和格式化增强可读性
3. 保持一致的样式风格

## 常见问题

### Q: 如何调试插件？
A: 使用 logger 记录日志，在 AstrBot 控制台查看输出。

### Q: 如何添加新的配置项？
A: 在 `_conf_schema.json` 中添加配置定义，在 `config.py` 中添加访问方法。

### Q: 如何处理异步操作？
A: 使用 `async/await` 语法，确保所有异步操作都正确处理。

## 贡献指南

欢迎提交 Issue 和 Pull Request！

在提交代码前，请确保：
1. 代码已通过 ruff 格式化
2. 所有测试通过
3. 添加了必要的注释
4. 更新了相关文档
