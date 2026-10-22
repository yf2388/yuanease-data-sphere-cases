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
- 问答题：`cases/01-supply-chain-network/questions.yaml` 中标注出处的题目改编自该仓库语义模型 `SUPPLY_CHAIN_ASSISTANT_MODEL.yaml` 的 verified_queries，以及配套指南的示例问题（问题意图与查询口径相同，改写为中文并把相对日期换成固定日期）。

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
- 问答题：`cases/02-cold-chain-ontology/questions.yaml` 中标注出处的题目取自 Microsoft Learn 本体教程（第 0、2、4 部分）的场景问题、业务规则与示例问句，改写为中文、不依赖上下文的问句；教程原文未复制。

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

以下数据集按知识共享 署名 4.0 国际许可协议（CC BY 4.0，<https://creativecommons.org/licenses/by/4.0/>）使用。改编内容见对应案例的 `prepare/build_data.py` 与 [PROVENANCE.md](PROVENANCE.md)。

| 用于 | 数据集 | 署名 | 来源 | 改动 |
|---|---|---|---|---|
| `cases/04-cnc-machine-failure` | AI4I 2020 Predictive Maintenance Dataset（UCI 页面写明为合成数据） | AI4I 2020 Predictive Maintenance Dataset (2020). UCI Machine Learning Repository. https://doi.org/10.24432/C5HS5C ；论文 S. Matzka (2020) | <https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset> | 列名汉化；按行序分配到 10 台设备并生成加工时间与班组；由失效模式标志派生故障事件表；叠加自建的设备台账、产线、班组、失效模式主数据 |
| `cases/07-garment-team-productivity` | Productivity Prediction of Garment Employees | Productivity Prediction of Garment Employees [Dataset]. (2020). UCI Machine Learning Repository. https://doi.org/10.24432/C51S6D ；论文 A. A. Imran, M. S. Rahim, T. Ahmed (2021), Mining the productivity data of the garment industry, International Journal of Business Intelligence and Data Mining 19(3) | <https://archive.ics.uci.edu/dataset/597/productivity+prediction+of+garment+employees> | 列名汉化，取值与行序不变；派生部门对照表与日历表 |
| `cases/09-steel-plant-energy` | Steel Industry Energy Consumption | V E, S., Shin, C., & Cho, Y. (2021). Steel Industry Energy Consumption [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C52G8C | <https://archive.ics.uci.edu/dataset/851/steel+industry+energy+consumption> | 只取 2018 年 1–3 月；列名汉化；时间格式改写；拆出日历表，叠加自建的负荷类型与班次表 |

## 5. Brunel University London：Supply Chain Logistics Problem Dataset（CC BY 4.0）

- 用于：`cases/08-supply-disruption`
- 署名：Kalganova, T., & Dzalbs, I. (2019). Supply Chain Logistics Problem Dataset. Brunel University London. Dataset. https://doi.org/10.17633/rd.brunel.7558679.v2 ；论文 I. Dzalbs, T. Kalganova (2020), Accelerating supply chains with Ant Colony Optimization across a range of hardware solutions, Computers & Industrial Engineering 147:106610
- 来源：<https://brunel.figshare.com/articles/dataset/Supply_Chain_Logistics_Problem_Dataset/7558679>
- 许可：CC BY 4.0（<https://creativecommons.org/licenses/by/4.0/>）
- 改动：7 个工作表各存成一个 CSV，表名、列名译为中文；订单日期写成 YYYY-MM-DD；去掉没有列名的空白列。取值未改。

## 6. 欧盟 Safety Gate 周报（CC BY 4.0）

- 用于：`cases/06-auto-quality-analysis`
- 署名：© European Union, Safety Gate – the EU rapid alert system for dangerous non-food products, <https://ec.europa.eu/safety-gate-alerts/>，2025 年第 1–52 期周报
- 许可：欧盟委员会网站法律声明（<https://commission.europa.eu/legal-notice_en>）规定其自有内容以 CC BY 4.0 授权，依据为 2011 年 12 月 12 日关于委员会文件再利用的委员会决定（2011/833/EU）。品牌名称、商标不在授权范围内，本仓库只把它们作为通报里的事实取值使用；周报里的产品图片未使用。
- 改动：只取产品类别为 Motor vehicles 的 448 条通报；字段名译为中文；派生周报表与通报风险表。通报文字未改。逐份周报的下载地址与 sha256 见 `cases/06-auto-quality-analysis/prepare/sources.tsv`。

## 7. 自建合成数据

`cases/10-order-metric-types` 的数据由 `prepare/build_data.py` 以固定随机数种子生成，全部为虚构内容，不涉及任何真实企业或个人，按本仓库 LICENSE 第 2 类（CC BY 4.0）授权。`cases/04-cnc-machine-failure` 的设备台账、产线、班组、失效模式主数据与加工时间同样为自建。

## 8. 问答题的公开出处（只借问题意图，不含数据）

下列案例 `questions.yaml` 里 `source` 标注了出处的题目（q11 起），问题意图或示例查询口径取自对应的公开文档；题干改写为中文、不依赖上下文的问句，原文与代码未复制，标准答案全部由本仓库 `data/` 上的 SQL 独立算出。

| 用于 | 出处 |
|---|---|
| `cases/03-bike-production-bom` | Microsoft Learn T-SQL 文档（WITH common_table_expression 示例 E、EXCEPT and INTERSECT 示例、FROM - Using PIVOT and UNPIVOT 的 Basic PIVOT example）；SQL Server 2005 文档 AdventureWorks Manufacturing Scenario 与 Product Scenario；AdventureWorks 安装脚本 instawdb.sql 的 ufnGetStock（MIT） |
| `cases/04-cnc-machine-failure` | Microsoft Learn「Fabric 数据科学：predictive maintenance」教程 Step 2、3、6 的数据说明与分析结论；UCI AI4I 2020 数据集页的失效模式说明 |
| `cases/05-purchasing-metrics` | Databricks 文档「Metric views TPC-H example」Step 8 的按月与状态查询；Microsoft Learn PIVOT 文档的 Complex PIVOT example（AdventureWorks 采购单） |
| `cases/08-supply-disruption` | Palantir 博客「Building with Palantir AIP」系列 Data Tools、Logic Tools 两篇的配送中心起火剧本（剧本步骤与提示词意图，改写为本案例数据上的仓库停运假设；博客数据与原文未使用） |
| `cases/10-order-metric-types` | dbt Semantic Layer 快速入门（docs.getdbt.com/guides/sl-qs）的示例查询与练习；dbt Labs 示例仓库 dbt-labs/jaffle-sl-template 的 saved queries 与 Evidence 报表查询 |
