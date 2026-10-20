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

- 用于：`cases/03-bike-production-bom`
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
