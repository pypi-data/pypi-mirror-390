# 🚀 MCP Data Analyzer ZSK

<div align="center">

![Version](https://img.shields.io/badge/version-0.1.1-blue.svg)
![Python](https://img.shields.io/badge/python-3.13+-green.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey.svg)
![MCP](https://img.shields.io/badge/MCP-1.21.0+-red.svg)

**一个基于 MCP (Model Context Protocol) 的强大数据分析与可视化工具**

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [工具使用](#-工具使用) • [可视化展示](#-可视化展示) • [贡献指南](#-贡献指南)

</div>

---

## 📋 目录

- [🌟 项目简介](#-项目简介)
- [✨ 功能特性](#-功能特性)
- [🚀 快速开始](#-快速开始)
- [🛠️ 工具使用](#️-工具使用)
- [📊 可视化展示](#-可视化展示)
- [💡 使用场景](#-使用场景)
- [📁 项目结构](#-项目结构)
- [🔧 技术栈](#-技术栈)
- [📝 更新日志](#-更新日志)
- [🤝 贡献指南](#-贡献指南)
- [📄 许可证](#-许可证)
- [👤 作者](#-作者)

---

## 🌟 项目简介

**MCP Data Analyzer ZSK** 是一个专为 AI 助手设计的数据分析与可视化工具，基于 [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) 构建。它能够快速处理 CSV、Excel 等格式的数据，生成专业的统计报告和多维度可视化图表。

### 核心价值

✨ **零门槛使用** - 简单配置即可在 MCP 客户端中使用
📊 **多维分析** - 支持 1-2 维数据透视分析，自动生成多种图表
🎨 **智能可视化** - 自动选择最佳图表类型，智能数字格式化
🌏 **跨平台支持** - 自动适配不同操作系统的中文字体
⚡ **高效处理** - 基于 pandas，毫秒级数据处理能力

---

## ✨ 功能特性

### 🔍 数据概览分析 (`data_overview`)
- ✅ 快速获取数据集基本信息（行数、列数）
- ✅ 自动检测字段类型（数值、类别、日期等）
- ✅ 统计缺失值情况
- ✅ 展示前 5 行样本数据
- ✅ JSON 格式输出，便于程序解析

### 📈 数据汇总统计 (`data_summary`)
- ✅ 数值列统计：均值、中位数、最大值、最小值、方差、标准差
- ✅ 类别列统计：唯一值数量、最常见值
- ✅ 缺失值详细分析
- ✅ 中文描述，便于理解

### 🎨 多维数据可视化 (`visualize_data`)
- ✅ **单维度分析**（1个索引列）
  - 📊 柱状图 - 直观显示数值分布
  - 🥧 饼图 - 清晰展示占比关系
- ✅ **双维度分析**（2个索引列）
  - 🔥 热力图 - 快速识别数据模式
  - 📚 堆叠柱状图 - 展示累计值和贡献比
  - 📊 分组柱状图 - 并排对比不同类别
- ✅ **多指标对比** - 同时分析多个数值列
- ✅ **智能数字格式化** - 自动使用万、百万、亿等单位
- ✅ **跨平台字体** - macOS/Windows/Linux 中文显示优化

### 🧠 智能特性
- 📐 支持多种聚合函数：`sum`、`mean`、`count`、`max`、`min`、`median`、`std`、`var`
- 🔤 自动 Unicode 解码，支持中文列名
- 💾 高分辨率图表输出（300 DPI）
- 🎯 自动布局优化，图表更美观

---

## 🚀 快速开始

### 系统要求

- **Python**: 3.13 或更高版本
- **操作系统**: macOS / Windows / Linux
- **内存**: 建议 2GB 以上

### 安装方式

#### 方式一：从源码安装（推荐）

```bash
# 克隆项目
git clone <your-repository-url>
cd mcp-data-analyzer

# 使用 uv 安装（推荐）
uv pip install -e .

# 或使用 pip
pip install -e .
```

#### 方式二：开发模式安装

```bash
# 安装开发依赖
uv pip install -e ".[dev]"
# 或
pip install -e ".[dev]"
```

### 启动 MCP 服务器

```bash
# 启动服务器
mcp-data-analyzer-zsk
```

### 配置 MCP 客户端

在您的 MCP 客户端配置文件中添加：

```json
{
  "mcpServers": {
    "data-analyzer": {
      "command": "mcp-data-analyzer-zsk",
      "args": []
    }
  }
}
```

---

## 🛠️ 工具使用

### 1️⃣ data_overview - 数据概览

获取数据集的基本信息和统计摘要。

**参数：**
- `data_path` (string, 必需): 数据文件路径，支持 `.csv`、`.xlsx`、`.xls`

**返回：**
- 数据集总行数和列数
- 列名及数据类型
- 缺失值统计
- 前 5 行样本数据

**示例：**
```json
{
  "tool": "data_overview",
  "arguments": {
    "data_path": "/path/to/sales.csv"
  }
}
```

**返回示例：**
```json
{
  "total_rows": 27,
  "total_columns": 11,
  "columns": ["销售日期", "销售员", "品牌", "车型", "客户城市", "售价", "销售量", "销售额"],
  "data_types": {
    "销售日期": "datetime64[ns]",
    "售价": "int64",
    "销售量": "int64"
  },
  "missing_values": {
    "销售日期": 0,
    "销售员": 0,
    "品牌": 0
  }
}
```

### 2️⃣ data_summary - 数据汇总

生成详细的数据统计摘要。

**参数：**
- `data_path` (string, 必需): 数据文件路径

**返回：**
- 数值列的描述性统计
- 类别列的频次分析
- 缺失值统计

**示例：**
```json
{
  "tool": "data_summary",
  "arguments": {
    "data_path": "/path/to/sales.xlsx"
  }
}
```

### 3️⃣ visualize_data - 数据可视化 ⭐

通过数据透视生成多维度可视化图表。

**参数：**
- `data_path` (string, 必需): 数据文件路径
- `index` (array, 必需): 透视索引列名列表（1-2 个维度）
  - 示例：`["城市"]` 或 `["城市", "季度"]`
- `values` (array, 必需): 需要聚合的数值列名列表
  - 示例：`["销量", "销售额"]`
- `aggfunc` (string, 可选): 聚合函数（默认 `"sum"`）
  - 支持：`sum`、`mean`、`count`、`max`、`min`、`median`、`std`、`var`
- `output_dir` (string, 可选): 图表保存目录（默认 `"./output"`）

**图表类型：**

| 索引维度 | 图表类型 | 适用场景 |
|---------|---------|----------|
| 1 维 | 柱状图 | 数值对比 |
| 1 维 | 饼图 | 占比分析 |
| 2 维 | 热力图 | 交叉分析 |
| 2 维 | 堆叠柱状图 | 累计展示 |
| 2 维 | 分组柱状图 | 并排对比 |
| 多值 | 对比图 | 多指标分析 |

**示例 1：单维度分析**
```json
{
  "tool": "visualize_data",
  "arguments": {
    "data_path": "sales.xlsx",
    "index": ["城市"],
    "values": ["销售额"],
    "aggfunc": "sum",
    "output_dir": "./output"
  }
}
```

**示例 2：双维度分析**
```json
{
  "tool": "visualize_data",
  "arguments": {
    "data_path": "sales.xlsx",
    "index": ["年份", "月份"],
    "values": ["销售额", "销售量"],
    "aggfunc": "mean",
    "output_dir": "./output"
  }
}
```

**示例 3：多指标对比**
```json
{
  "tool": "visualize_data",
  "arguments": {
    "data_path": "sales.xlsx",
    "index": ["品牌"],
    "values": ["销售额", "利润", "订单数"],
    "aggfunc": "sum"
  }
}
```

---

## 📊 可视化展示

以下是基于真实销售数据生成的示例图表：

### 📈 单维度分析

#### 月度销售趋势
![月度销售额柱状图](output/bar_销售月份_销售额_sum.png)
![月度销售额饼图](output/pie_销售月份_销售额_sum.png)

#### 品牌销售对比
![品牌销售额柱状图](output/bar_品牌_销售额_sum.png)
![品牌销售量饼图](output/pie_品牌_销售量_sum.png)

### 🔥 双维度分析

#### 时间交叉分析
![年份×月份热力图](output/heatmap_销售年份_销售月份_2890000_sum.png)
![年份×月份堆叠柱状图](output/stacked_bar_销售年份_销售月份_2890000_sum.png)
![年份×月份分组柱状图](output/grouped_bar_销售年份_销售月份_2890000_sum.png)

### 📊 多指标对比
![多指标对比图](output/multi_value_comparison_sum.png)

### 💡 图表特色

- **智能数字格式化** - 自动将大数字转换为万、百万、亿等单位
- **高分辨率输出** - 300 DPI 适合打印和演示
- **中文优化** - 跨平台中文字体自动适配
- **数值标签** - 图表上直接显示数值，便于阅读
- **配色优化** - 使用专业配色方案，视觉舒适

---

## 💡 使用场景

### 📊 商业分析
- **销售数据分析** - 分析销售额、销售量趋势
- **市场研究** - 对比不同地区、品牌的市场表现
- **用户行为分析** - 分析用户购买偏好、活跃度

### 📈 数据科学
- **探索性数据分析 (EDA)** - 快速理解数据分布
- **特征工程** - 识别数据模式和异常值
- **报告生成** - 自动生成可视化分析报告

### 🎓 教育培训
- **统计教学** - 直观展示统计概念
- **数据可视化** - 多种图表类型展示
- **案例分析** - 真实数据案例研究

### 🏢 企业应用
- **运营报告** - 自动化运营数据分析
- **KPI 监控** - 关键指标可视化追踪
- **决策支持** - 数据驱动的业务决策

---

## 📁 项目结构

```
mcp-data-analyzer/
├── 📦 mcp_data_analyzer_zsk/          # 主包目录
│   ├── __init__.py                    # 包初始化
│   ├── __main__.py                    # 模块入口
│   ├── cli.py                         # CLI 接口
│   └── core.py                        # 核心逻辑
├── 📂 output/                         # 图表输出目录
│   ├── *.png                          # 生成的可视化图表
│   └── sales_analysis_report.md       # 示例分析报告
├── 📄 pyproject.toml                  # 项目配置
├── 📄 README.md                       # 项目文档
├── 📄 uv.lock                         # 依赖锁定文件
└── 📄 LICENSE                         # 许可证
```

---

## 🔧 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **MCP** | ≥ 1.21.0 | 协议框架 |
| **pandas** | ≥ 2.3.3 | 数据处理 |
| **matplotlib** | 内置 | 图表绘制 |
| **seaborn** | ≥ 0.13.2 | 统计可视化 |
| **openpyxl** | ≥ 3.1.0 | Excel 文件支持 |
| **Python** | ≥ 3.13 | 开发语言 |

---

## 📝 更新日志

### v0.1.1 (2024-11-08)
- ✨ 优化中文字体支持
- ✨ 改进数字格式化逻辑
- ✨ 增强错误处理机制
- 📝 完善文档

### v0.1.0 (2024-11-08)
- 🎉 首次发布
- ✨ 支持 data_overview 数据概览
- ✨ 支持 data_summary 数据汇总
- ✨ 支持 visualize_data 多维可视化
- ✨ 支持 CSV、Excel 格式
- ✨ 支持 5 种图表类型
- ✨ 跨平台中文字体支持

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 🐛 报告问题
如果您发现任何问题，请提交 [Issue](../../issues)，包含：
- 详细的问题描述
- 复现步骤
- 预期行为
- 截图（如有）
- 环境信息

### 💡 提出功能建议
欢迎提出新功能建议！请在 [Issue](../../issues) 中描述：
- 功能描述
- 使用场景
- 预期效果

### 🔧 提交代码
1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'feat: add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 提交 Pull Request

### 📋 开发环境设置

```bash
# 克隆仓库
git clone <repository-url>
cd mcp-data-analyzer

# 创建虚拟环境
uv venv
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate  # Windows

# 安装开发依赖
uv pip install -e ".[dev]"
```

---

## 📄 许可证

本项目基于 **MIT 许可证** 开源。详情请查看 [LICENSE](LICENSE) 文件。

```
MIT License

Copyright (c) 2024 zsk

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## 👤 作者

**zsk** - *初始开发* - MCP Data Analyzer ZSK

---

## 🙏 致谢

感谢以下优秀的开源项目：

- [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) - 强大的协议框架
- [pandas](https://pandas.pydata.org/) - 数据分析基础库
- [matplotlib](https://matplotlib.org/) - 图表绘制
- [seaborn](https://seaborn.pydata.org/) - 统计数据可视化

---

## 📞 联系我们

如有问题或建议，欢迎通过以下方式联系：

- 📧 邮箱：[your-email@example.com]
- 🐛 问题反馈：[提交 Issue](../../issues)
- 💬 讨论区：[Discussions](../../discussions)

---

## ⭐ 支持我们

如果这个项目对您有帮助，请给我们一个 ⭐ Star！

您的支持是我们持续改进的动力！

---

<div align="center">

**Built with ❤️ by zsk**

[⬆ 回到顶部](#-mcp-data-analyzer-zsk)

</div>