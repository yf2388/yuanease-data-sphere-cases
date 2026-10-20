# 第三方数据与许可声明

本仓库部分案例的数据改编自下列公开数据集。各数据集按其原始许可证使用与再分发；对数据所做的改动写在每个案例的 `prepare/build_data.py` 文件头，以及对应案例 README 的「数据来源与改动」一节。

本仓库不包含任何竞品教程的文字、截图或配置文件；源自竞品公开教程的案例只复现其业务场景与问题清单，并在案例 README 中注明出处链接。

---

## 1. Snowflake 供应链助手示例数据

- 用于：`cases/01-supply-chain-network`
- 来源：<https://github.com/Snowflake-Labs/sfguide-supply-chain-assistant-with-snowflake-intelligence>（`scripts/setup.sql` 中的 INSERT 数据）
- 许可：MIT License，Copyright (c) 2025 Snowflake Inc.
- 仓库附带的 LEGAL.md 说明：该应用不属于 Snowflake 服务，受 LICENSE 条款约束，使用风险自负，Snowflake 无支持义务。
- 改动：表名、列名译为中文；布尔值写成「是/否」；时间戳去掉时区后缀；不含天气表与会话表。

```
MIT License

Copyright (c) 2025 Snowflake Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 2. Microsoft Fabric 本体（Ontology）教程示例数据（Lakeshore Retail）

- 用于：`cases/02-cold-chain-ontology`
- 来源：<https://github.com/microsoft/fabric-samples/tree/main/docs-samples/iq/ontology/new-experience>
- 许可：MIT License，Copyright (c) Microsoft Corporation.
- 改动：表名、列名译为中文；布尔值写成「是/否」；ISO 时间戳写成「YYYY-MM-DD HH:MM:SS」（仍为 UTC）；不含 SalesReport.pbix。

```
MIT License

Copyright (c) Microsoft Corporation.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE
```

## 3. Microsoft AdventureWorks 示例数据库

- 用于：`cases/03-bike-production-bom`、`cases/05-purchasing-metrics`
- 来源：<https://github.com/microsoft/sql-server-samples/tree/master/samples/databases/adventure-works/oltp-install-script>
- 许可：MIT License，「Microsoft SQL Server Sample Code，Copyright (c) Microsoft Corporation」（仓库根目录 license.txt；子目录无单独声明，适用仓库级许可）。
- 改动：见各案例 `prepare/build_data.py`（列名汉化、去掉审计列、按开工日期抽样等）。

```
Microsoft SQL Server Sample Code

Copyright (c) Microsoft Corporation

All rights reserved.

MIT License.

Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
 all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 THE SOFTWARE.
```

## 4. UCI 机器学习库数据集（CC BY 4.0）

以下数据集按知识共享 署名 4.0 国际许可协议（CC BY 4.0，<https://creativecommons.org/licenses/by/4.0/>）使用。改编内容见对应案例的 `prepare/build_data.py`。

| 用于 | 数据集 | 署名 | 来源 | 改动 |
|---|---|---|---|---|
| `cases/04-cnc-machine-failure` | AI4I 2020 Predictive Maintenance Dataset | AI4I 2020 Predictive Maintenance Dataset (2020). UCI Machine Learning Repository. https://doi.org/10.24432/C5HS5C ；论文 S. Matzka (2020) | <https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset> | 列名汉化；按行序分配到 10 台设备并生成加工时间与班组；由失效模式标志派生故障事件表；叠加自建的设备台账、产线、班组、失效模式主数据 |
| `cases/09-steel-plant-energy` | Steel Industry Energy Consumption | V E, S., Shin, C., & Cho, Y. (2021). Steel Industry Energy Consumption [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C52G8C | <https://archive.ics.uci.edu/dataset/851/steel+industry+energy+consumption> | 只取 2018 年 1–3 月；列名汉化；时间格式改写；拆出日历表，叠加自建的负荷类型与班次表 |

## 5. 自建合成数据

`cases/06-auto-quality-analysis`、`cases/07-multi-plant-oee`、`cases/08-supply-disruption`、`cases/10-order-metric-types` 的数据由各自 `prepare/build_data.py` 以固定随机数种子生成，全部为虚构内容，不涉及任何真实企业或个人，按本仓库 LICENSE 第 2 类（CC BY 4.0）授权。
