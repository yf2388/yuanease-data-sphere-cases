# 数据来源与可复现性

本页回答三件事：每个案例的数据从哪来、按什么许可使用、相对原始文件做了哪些改动，以及怎样从原始文件逐字节复现 `data/`。
核查日期 2026-10-22：下表所有原始文件都在这一天按官方地址重新下载，`prepare/build_data.py` 生成的 CSV 与仓库里的 `data/` 逐字节一致（sha256 相同）。

## 三档来源

选数据源的优先顺序：①竞品厂商自己公开的演示数据（复现竞品演示最有说服力），②开源社区的语义层 / 本体项目数据，③政府与公共机构的开放数据；许可没核实到原文的一律不用。06、10 复现的是 Google Malloy 的官方演示；07、08、11 没找到许可可用的厂商演示数据（Databricks、Siemens 的样例限定只能在自家平台使用，Palantir 没有可下载的数据，Snowflake、AWS 的同类样例只有运行时随机生成的代码），改用研究机构与监管机构公开的真实数据。

成绩按数据来源分三档报告（见顶层 README 的实测汇总）。主指标只看前两档。

| 档位 | 含义 | 案例 |
|---|---|---|
| 真实测量 | 原始数据是真实生产经营活动的记录，由企业、研究机构或监管机构公开发布 | 06、07、08、09、11 |
| 厂商样例 | 软件厂商为教程与演示公开发布的样例数据库：公司与数据是虚构的，但出自第三方，可从原始文件逐字节复现，不是本仓库编的 | 01、02、03、05、10 |
| 虚构 | 数据由本仓库自建，或者表结构与关键列由本仓库自建 | 04 |

## 逐案例

| 案例 | 档位 | 原始数据 | 许可 | 相对原始文件的改动 |
|---|---|---|---|---|
| 01 | 厂商样例 | Snowflake 供应链助手指南 `scripts/setup.sql` 里的 INSERT 数据 | MIT | 表名、列名译成中文；布尔值写成「是/否」；时间戳去掉时区后缀；NULL 写成空；不含天气表与会话表。行与取值不变 |
| 02 | 厂商样例 | Microsoft fabric-samples 本体教程（Lakeshore Retail）的 7 个 CSV | MIT | 表名、列名译成中文；布尔值写成「是/否」；ISO 时间戳写成「YYYY-MM-DD HH:MM:SS」（仍为 UTC）。行与取值不变 |
| 03 | 厂商样例 | Microsoft AdventureWorks OLTP 安装脚本的生产相关 11 张表 | MIT | 列名译成中文；去掉审计列与 XML 列；工位、报废原因、产品大类与子类的名称译成中文（对照表在脚本里）；标志位写成「是/否」；日期只留年月日（原始时分秒都是 0）；**裁剪行**：工单只取开工日期在 2025 年 5 月的 3,432 张及其工序 |
| 04 | 虚构 | UCI AI4I 2020 预测性维护数据（UCI 数据集页写明是合成数据）+ 本仓库自建的设备、产线、班组、失效模式主数据 | CC BY 4.0（UCI 部分） | 原始 10,000 行的测量列不变；**设备编号、加工时间、班组由本仓库按规则分配**，故障事件表由五个失效标志派生，四张主数据表自建 |
| 05 | 厂商样例 | Microsoft AdventureWorks OLTP 安装脚本的采购相关 5 张表与 4 张维表 | MIT | 列名译成中文；去掉审计列，产品表只留 8 列；采购单状态码按建库脚本的列说明写成中文；产品大类与子类名称译成中文；标志位、日期同 03。全量，不裁剪 |
| 06 | 真实测量 | Google Malloy 官方样例 malloydata/malloy-samples 的 auto_recalls 演示：美国 NHTSA 的全量召回记录（Malloy README 注明取自 catalog.data.gov 的 recalls-data），本案例取 2021-01 至 2022-06 的 1,574 条 | MIT（样例仓库）；底层为美国联邦政府作品（公有领域） | **裁剪行**：只取报告接收日期在 2021 年及以后的召回；列名译成中文；派生日历表，以及部件、召回类型两张中文译名对照表。召回记录原样保留 |
| 07 | 真实测量 | UCI「Productivity Prediction of Garment Employees」：一家服装企业 2015 年 1–3 月 1,197 条班组日报（UCI 页面说明由人工采集、经行业专家核验） | CC BY 4.0 | 班组日报逐行逐列照搬，只译列名，连原始拼写（sweing）与尾随空格都保留；派生部门对照表（3 种原始写法 → 缝制 / 后整）与日历表 |
| 08 | 真实测量 | Brunel University London「Supply Chain Logistics Problem Dataset」：一家全球芯片制造商提供的出库物流数据（论文 Dzalbs & Kalganova 2020 第 4 节），9,215 张订单、19 个仓库 | CC BY 4.0 | 7 个工作表各存一个 CSV，只译表名、列名；订单日期单元格写成「YYYY-MM-DD」；去掉工作表右侧没有列名的空白列。数字与文字取值不变 |
| 09 | 真实测量 | UCI「Steel Industry Energy Consumption」：韩国 DAEWOO Steel 光阳工厂的 15 分钟用电记录（UCI 页面说明数据存放在 KEPCO 网站） | CC BY 4.0 | **裁剪行**：只取 2018 年 1–3 月；列名译成中文；时间写成「YYYY-MM-DD HH:MM」；记录编号按原始行序编；按时段派生班次代码（班次划分规则是本仓库定的，写在脚本里）；派生日历表、负荷类型代码表与班次表。用电量等测量值不变 |
| 10 | 厂商样例 | Google Malloy 官方样例 malloydata/malloy-samples 的 thelook 电商演示数据（Looker / Google 用来演示语义层的虚构电商数据库） | MIT | **裁剪行**：只取所在州为 Florida 的 5,740 个用户及其全部 9,448 件订单明细、引用到的库存件与商品；**去列**：用户表不带姓名、邮箱、邮编、经纬度；表名列名译成中文；时间写成「YYYY-MM-DD HH:MM:SS」。数字与文字取值不变 |
| 11 | 真实测量 | 欧盟 Safety Gate 2025 年 52 份周报里的 448 条机动车召回通报（各国市场监管机构通报、欧盟委员会发布） | CC BY 4.0（欧盟委员会网站内容） | **裁剪行**：只取产品类别为 Motor vehicles 的通报；字段名译成中文；不含图片与三个全空字段；派生周报表与通报风险表（复合风险类型按「, 」拆行）。通报文字原样保留，含首尾空格 |

每个案例 `prepare/build_data.py` 的文件头逐条写了改动；06、07、08、10、11 另有 `prepare/truth_from_raw.py`，不经 `data/` 与 SQL，直接从原始文件重算全部标准答案并与 `questions.yaml` 比对。

## 原始文件清单

GitHub 上的文件钉在下载时该路径最近一次提交的 commit，任何时候按这个地址下载都应得到同一个 sha256。

| 案例 | 文件 | 地址 | 许可 | 字节 | sha256 |
|---|---|---|---|---:|---|
| 01 | LEGAL.md | https://raw.githubusercontent.com/Snowflake-Labs/sfguide-supply-chain-assistant-with-snowflake-intelligence/b436f13e32773ec4ccaaaba3bce9fba4ee6cc32a/LEGAL.md | MIT（LICENCE） | 249 | `46d66708fcd4502c5fbb923f6bf61061ed7e67f5148c7573a7893782cda490f9` |
| 01 | LICENCE | https://raw.githubusercontent.com/Snowflake-Labs/sfguide-supply-chain-assistant-with-snowflake-intelligence/b436f13e32773ec4ccaaaba3bce9fba4ee6cc32a/LICENCE | MIT（LICENCE） | 1,070 | `d4d04616f38023429967317213a423e0ed4f76a4a6bdb67a8fe66f6f00c01b66` |
| 01 | SUPPLY_CHAIN_ASSISTANT_MODEL.yaml | https://raw.githubusercontent.com/Snowflake-Labs/sfguide-supply-chain-assistant-with-snowflake-intelligence/6a1872bd44956f73c1f862664ad97bcf4d593415/scripts/semantic_models/SUPPLY_CHAIN_ASSISTANT_MODEL.yaml | MIT（LICENCE） | 53,252 | `62660acd25de03b8460093fea18177cf446a3a226757b9e1bc3ba295aa8b3328` |
| 01 | setup.sql | https://raw.githubusercontent.com/Snowflake-Labs/sfguide-supply-chain-assistant-with-snowflake-intelligence/adcda446d9b22f40f3f184bddc65ff6dc48ed30e/scripts/setup.sql | MIT（LICENCE） | 630,842 | `a0bd4bbd65e2270c4add139cb1f5ef9902840071df034adfdce35531d4e9503f` |
| 02 | LICENSE | https://raw.githubusercontent.com/microsoft/fabric-samples/58e3a8fb29706b533e11b5cf263fb4bd5eed8d85/LICENSE | MIT（仓库根 LICENSE） | 1,141 | `c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383` |
| 02 | dim_refrigeration_units.csv | https://raw.githubusercontent.com/microsoft/fabric-samples/805b3abfe17abf373cef1904f07d762ab001ced2/docs-samples/iq/ontology/new-experience/dim_refrigeration_units.csv | MIT（仓库根 LICENSE） | 948 | `996f8a6bb926e5458d1397dbd457177c898ac6f520456f36d94805e0069c983a` |
| 02 | dimlocations.csv | https://raw.githubusercontent.com/microsoft/fabric-samples/805b3abfe17abf373cef1904f07d762ab001ced2/docs-samples/iq/ontology/new-experience/dimlocations.csv | MIT（仓库根 LICENSE） | 953 | `6a2571652229b9b0ec5c9813fc66c40e20ff8fbd80ac60daffe1b532929e5ce9` |
| 02 | dimproducts.csv | https://raw.githubusercontent.com/microsoft/fabric-samples/805b3abfe17abf373cef1904f07d762ab001ced2/docs-samples/iq/ontology/new-experience/dimproducts.csv | MIT（仓库根 LICENSE） | 1,000 | `16a575426e93cddb314b68cfe92c57eaf1bd4b114d9c9c4c373f629ddb658aaf` |
| 02 | dimsuppliers.csv | https://raw.githubusercontent.com/microsoft/fabric-samples/805b3abfe17abf373cef1904f07d762ab001ced2/docs-samples/iq/ontology/new-experience/dimsuppliers.csv | MIT（仓库根 LICENSE） | 335 | `73761fcb86a2ac0cdabc188b55f4341c2294ccec593f0937ba5009d77aab8e59` |
| 02 | fact_inventory_positions.csv | https://raw.githubusercontent.com/microsoft/fabric-samples/805b3abfe17abf373cef1904f07d762ab001ced2/docs-samples/iq/ontology/new-experience/fact_inventory_positions.csv | MIT（仓库根 LICENSE） | 4,021 | `4e748be964f3ab8f05d014e5cc3778890b3fd03a47d863fabaaf957a0c46159b` |
| 02 | factshipments.csv | https://raw.githubusercontent.com/microsoft/fabric-samples/805b3abfe17abf373cef1904f07d762ab001ced2/docs-samples/iq/ontology/new-experience/factshipments.csv | MIT（仓库根 LICENSE） | 1,069 | `d4a4c050b9b1517356ad957a2872eb158452426e33ef7096b63bb7dc97fd4eca` |
| 02 | refrigeration_telemetry.csv | https://raw.githubusercontent.com/microsoft/fabric-samples/805b3abfe17abf373cef1904f07d762ab001ced2/docs-samples/iq/ontology/new-experience/refrigeration_telemetry.csv | MIT（仓库根 LICENSE） | 224,693 | `af996c193178b79ca0b64e758de6320fa49029b0fec26676b43e396b7a196321` |
| 03、05 | BillOfMaterials.csv | https://raw.githubusercontent.com/microsoft/sql-server-samples/b47eadc85277f72843647223cde53aa1b85ffcb8/samples/databases/adventure-works/oltp-install-script/BillOfMaterials.csv | MIT（仓库根 license.txt） | 198,923 | `a27765426bd4ee19ffb62150d087de88d2a199fddb55ffad55c2479079844c71` |
| 03、05 | Location.csv | https://raw.githubusercontent.com/microsoft/sql-server-samples/b47eadc85277f72843647223cde53aa1b85ffcb8/samples/databases/adventure-works/oltp-install-script/Location.csv | MIT（仓库根 license.txt） | 752 | `7bb94b3313fa91dcf451b5a4f43f31bc2b5061a1c9370849a0ba1234ba5a0d47` |
| 03、05 | Product.csv | https://raw.githubusercontent.com/microsoft/sql-server-samples/b47eadc85277f72843647223cde53aa1b85ffcb8/samples/databases/adventure-works/oltp-install-script/Product.csv | MIT（仓库根 license.txt） | 88,536 | `df0379a7cba8b11b97ea5d104cf1313ef9f683137b6426f2fac6bb8c74c2a2ea` |
| 03、05 | ProductCategory.csv | https://raw.githubusercontent.com/microsoft/sql-server-samples/b47eadc85277f72843647223cde53aa1b85ffcb8/samples/databases/adventure-works/oltp-install-script/ProductCategory.csv | MIT（仓库根 license.txt） | 290 | `d86dde135e023960633ed1d6a2fb72f56b74aa2f7d07af983b6bff5e33dfceb2` |
| 03、05 | ProductInventory.csv | https://raw.githubusercontent.com/microsoft/sql-server-samples/b47eadc85277f72843647223cde53aa1b85ffcb8/samples/databases/adventure-works/oltp-install-script/ProductInventory.csv | MIT（仓库根 license.txt） | 81,385 | `0eb400b3a9f0abea533ca91746950ac18ec01788ace01fd1b5cfa729904c2e86` |
| 03、05 | ProductModel.csv | https://raw.githubusercontent.com/microsoft/sql-server-samples/b47eadc85277f72843647223cde53aa1b85ffcb8/samples/databases/adventure-works/oltp-install-script/ProductModel.csv | MIT（仓库根 license.txt） | 53,533 | `f5acbcad41dd11b231bfa672116d58d1a59f660d4d49ee998ffc10c545bd031d` |
| 03、05 | ProductSubcategory.csv | https://raw.githubusercontent.com/microsoft/sql-server-samples/b47eadc85277f72843647223cde53aa1b85ffcb8/samples/databases/adventure-works/oltp-install-script/ProductSubcategory.csv | MIT（仓库根 license.txt） | 2,799 | `a90dce80f310044b99a920790cbf60b83982079af421a5935fda7bc7ab69bc75` |
| 03、05 | ProductVendor.csv | https://raw.githubusercontent.com/microsoft/sql-server-samples/b47eadc85277f72843647223cde53aa1b85ffcb8/samples/databases/adventure-works/oltp-install-script/ProductVendor.csv | MIT（仓库根 license.txt） | 40,182 | `d66c695e30deeb206f3b329a922fea905b42078ef9cbf546c421b49789bcc6fe` |
| 03、05 | PurchaseOrderDetail.csv | https://raw.githubusercontent.com/microsoft/sql-server-samples/b47eadc85277f72843647223cde53aa1b85ffcb8/samples/databases/adventure-works/oltp-install-script/PurchaseOrderDetail.csv | MIT（仓库根 license.txt） | 868,775 | `4e2e27e7a165bf1aa7e7675a7eebcb25c22a1c7bd0e2e3d7ce0f8ff53060c2d9` |
| 03、05 | PurchaseOrderHeader.csv | https://raw.githubusercontent.com/microsoft/sql-server-samples/b47eadc85277f72843647223cde53aa1b85ffcb8/samples/databases/adventure-works/oltp-install-script/PurchaseOrderHeader.csv | MIT（仓库根 license.txt） | 516,974 | `fd3b6d356238c5adc938e427fd5c523ee9e405fba1343852dfba85a0a888113c` |
| 03、05 | ScrapReason.csv | https://raw.githubusercontent.com/microsoft/sql-server-samples/b47eadc85277f72843647223cde53aa1b85ffcb8/samples/databases/adventure-works/oltp-install-script/ScrapReason.csv | MIT（仓库根 license.txt） | 780 | `cc0cab5472e4f94922500329286677c6209fe77114e1d6edcf713d1cf5919e8f` |
| 03、05 | ShipMethod.csv | https://raw.githubusercontent.com/microsoft/sql-server-samples/b47eadc85277f72843647223cde53aa1b85ffcb8/samples/databases/adventure-works/oltp-install-script/ShipMethod.csv | MIT（仓库根 license.txt） | 471 | `e366e56c63165a300a314fcba1237f54f2d0b94b4a3eb88bd15fb0437c2a37cb` |
| 03、05 | UnitMeasure.csv | https://raw.githubusercontent.com/microsoft/sql-server-samples/b47eadc85277f72843647223cde53aa1b85ffcb8/samples/databases/adventure-works/oltp-install-script/UnitMeasure.csv | MIT（仓库根 license.txt） | 1,424 | `6e4d07534b6900f035c3b5200880a9b54190e3db63c13280e1e98788178fdeb7` |
| 03、05 | Vendor.csv | https://raw.githubusercontent.com/microsoft/sql-server-samples/b47eadc85277f72843647223cde53aa1b85ffcb8/samples/databases/adventure-works/oltp-install-script/Vendor.csv | MIT（仓库根 license.txt） | 7,161 | `075c70b53fc860bf4a562b56df027b961ac4051f0fd0b75faaa106b5dae110e3` |
| 03、05 | WorkOrder.csv | https://raw.githubusercontent.com/microsoft/sql-server-samples/b47eadc85277f72843647223cde53aa1b85ffcb8/samples/databases/adventure-works/oltp-install-script/WorkOrder.csv | MIT（仓库根 license.txt） | 8,239,894 | `e6618bf291defe9fa645d795b1a951ecdfc04bc88746b12b196337485b2289b1` |
| 03、05 | WorkOrderRouting.csv | https://raw.githubusercontent.com/microsoft/sql-server-samples/b47eadc85277f72843647223cde53aa1b85ffcb8/samples/databases/adventure-works/oltp-install-script/WorkOrderRouting.csv | MIT（仓库根 license.txt） | 10,598,429 | `1e15eed408d37ca355167e505b4b1e65cfabf4909f92abe54839b158453f9000` |
| 03、05 | instawdb.sql | https://raw.githubusercontent.com/microsoft/sql-server-samples/1346b94fab23bfa7edfdb32afae52282ddc3bfaa/samples/databases/adventure-works/oltp-install-script/instawdb.sql | MIT（仓库根 license.txt） | 329,368 | `d979f036750f9c7b4fb7be3d58cdbb596a74f864a6325998501b3a96c6ad53f9` |
| 03、05 | license.txt | https://raw.githubusercontent.com/microsoft/sql-server-samples/4693087abebd7e835f9ee46d005dcdaa03092a40/license.txt | MIT（仓库根 license.txt） | 1,142 | `201f3705979e932c92cd3c6ddbddf4dc3c71dcc5a82089a1e4018227cfe1cf09` |
| 04 | ai4i.zip | https://archive.ics.uci.edu/static/public/601/ai4i+2020+predictive+maintenance+dataset.zip | CC BY 4.0 | 522,170 | `f601f14294bcf190f9d720676b7f0aea46a26cde9ab8ebc7b4f8174d9d26b252` |
| 04 | unzipped/ai4i2020.csv | 解压自 ai4i.zip | CC BY 4.0 | 522,048 | `dc6630cd9b1f0f853922fad78a1b6436570d3f1ec863f1dd5c4340ac56bc8a8e` |
| 09 | steel-energy.zip | https://archive.ics.uci.edu/static/public/851/steel+industry+energy+consumption.zip | CC BY 4.0 | 481,973 | `d82d28b33780ff1582507fcf08ae764ff648af459d58234370c551e62aadeaef` |
| 09 | unzipped/Steel_industry_data.csv | 解压自 steel-energy.zip | CC BY 4.0 | 2,731,389 | `9b1cee6f9cb9cd9df2b95814ca90a9a2ff15b7f5f1fba0fae3c643e82072eacc` |
| 06、10 | LICENSE | https://raw.githubusercontent.com/malloydata/malloy-samples/89eb0fda584e3b146bf04e2d31585d8f9b6ab7ec/LICENSE | MIT | 1,050 | `350805cc9dd73c357eb7e24459349e5952b2982bd9807a46e9295eca9d7d8d0f` |
| 06 | auto_recalls/auto_recalls.csv | https://raw.githubusercontent.com/malloydata/malloy-samples/89eb0fda584e3b146bf04e2d31585d8f9b6ab7ec/auto_recalls/auto_recalls.csv | MIT | 20,212,040 | `80fbb74a475789d277c4cc48f9e38eca97152ca6086a6f3f31893e491c2ab713` |
| 06 | auto_recalls/auto_recalls.malloy（Malloy 语义模型，问题出处，不生成数据） | https://raw.githubusercontent.com/malloydata/malloy-samples/89eb0fda584e3b146bf04e2d31585d8f9b6ab7ec/auto_recalls/auto_recalls.malloy | MIT | 1,894 | `cd1e4c48913194ea3d561b8e84d5cc9209d8c36aced0522223dae63b4dab8d1d` |
| 10 | ecommerce/ecommerce.malloy（Malloy 语义模型，问题出处，不生成数据） | https://raw.githubusercontent.com/malloydata/malloy-samples/89eb0fda584e3b146bf04e2d31585d8f9b6ab7ec/ecommerce/ecommerce.malloy | MIT | 5,322 | `15e62e72158cd05d0f9b7fb0e026d3c5a615dbc91dfc394bcebc5152e20650f3` |
| 10 | data/users.parquet | https://raw.githubusercontent.com/malloydata/malloy-samples/89eb0fda584e3b146bf04e2d31585d8f9b6ab7ec/data/users.parquet | MIT | 7,799,066 | `bf9da156bca2bc633ec41be202821b49cd25fcd185e37e936d588693468ca3db` |
| 10 | data/order_items.parquet | https://raw.githubusercontent.com/malloydata/malloy-samples/89eb0fda584e3b146bf04e2d31585d8f9b6ab7ec/data/order_items.parquet | MIT | 5,959,529 | `c86656d938dd4f10e67976142c8f9cc4ab2f0d5aaa8cd4f3c4345dc95c964d3d` |
| 10 | data/inventory_items.parquet | https://raw.githubusercontent.com/malloydata/malloy-samples/89eb0fda584e3b146bf04e2d31585d8f9b6ab7ec/data/inventory_items.parquet | MIT | 5,801,065 | `48a5fb48f5a45e6b3f165ac863f18859bf501cb53e2520596ca047c8d2ed39d8` |
| 10 | data/products.parquet | https://raw.githubusercontent.com/malloydata/malloy-samples/89eb0fda584e3b146bf04e2d31585d8f9b6ab7ec/data/products.parquet | MIT | 1,486,682 | `6d7e3f74c6da80eb5a0fc028b416f4be8ea9d0a68e8eb0dc7960400ae2314e5c` |
| 11 | list-en.xml（周报索引，只用其中 2025 年的 52 条） | https://ec.europa.eu/safety-gate-alerts/api/download/weeklyReport/list/xml/en | CC BY 4.0 | 391,177 | `d4f7c422e254e7a449e4406f912485052cd239a9c1c5d1f9cc5d012ec2d33161`（索引每周追加新周报，此值只对 2026-10-22 的下载有效） |
| 11 | weekly/Report-2025-1.xml … Report-2025-52.xml | 逐份地址与 sha256 见 `cases/11-eu-vehicle-recalls/prepare/sources.tsv`（重复下载内容相同） | CC BY 4.0 | — | — |
| 07 | productivity+prediction+of+garment+employees.zip | https://archive.ics.uci.edu/static/public/597/productivity+prediction+of+garment+employees.zip | CC BY 4.0 | 95,095 | `446026846b37d73800d1fd01b852ceaf95f086f15a626802d784154f63885bc2` |
| 07 | garments_worker_productivity.csv（解压自上面的 zip） | 同上 | CC BY 4.0 | 94,933 | `763ffcdd39b7f7f360243c2af8f89ed733e8b5f9e511efeb0c886b83e1b76866` |
| 08 | Supply chain logisitcs problem.xlsx | https://ndownloader.figshare.com/files/20162015（figshare 记录 https://doi.org/10.17633/rd.brunel.7558679.v2，页面给出的 MD5 `2a05e8f60a6dda8ac318084f4183b29f` 与下载文件一致） | CC BY 4.0 | 794,602 | `ae9af5248202d147e8a3514c30d81542db628009544e5accafb59452a5d24d3f` |

许可原文：Snowflake 与 Fabric 为仓库根目录的 MIT LICENSE；AdventureWorks 为仓库根目录 `license.txt`（开头是「Microsoft SQL Server Sample Code」，正文是 MIT 条款，GitHub 的许可识别因此显示 NOASSERTION）；
UCI 三个数据集页写明 CC BY 4.0；figshare 记录写明 CC BY 4.0；Malloy 样例仓库为 MIT（Copyright 2023 Google LLC）；欧盟委员会网站法律声明写明其自有内容以 CC BY 4.0 授权（品牌名称与商标不在授权范围内，本仓库只把它们作为通报里的事实取值使用）。
署名与原始许可全文见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

## 怎样复现

以案例 07 为例（需要 Python 3.9+ 与 PyYAML；08 另需 openpyxl，10 另需 pyarrow）：

```bash
mkdir -p /tmp/garment && cd /tmp/garment
curl -LO 'https://archive.ics.uci.edu/static/public/597/productivity+prediction+of+garment+employees.zip'
unzip productivity+prediction+of+garment+employees.zip
cd -   # 回到仓库根目录
python3 -I cases/07-garment-team-productivity/prepare/build_data.py /tmp/garment/garments_worker_productivity.csv /tmp/out07
diff -r /tmp/out07 cases/07-garment-team-productivity/data && echo 与仓库一致
python3 -I cases/07-garment-team-productivity/prepare/truth_from_raw.py /tmp/garment/garments_worker_productivity.csv
```

其余案例同理：按上表下载原始文件，参数写法见各案例 `prepare/build_data.py` 文件头的「用法」。11 需要先按 `prepare/sources.tsv` 把 52 份周报下载到 `weekly/` 目录，并把周报索引存成 `list-en.xml`；06、10 从 Malloy 样例仓库按上表地址下载（10 的参数是放 4 个 parquet 的目录）。

## 说明

- 01：原指南的 `setup.sql` 在建库时会执行 UPDATE，把订单、发货、库存等日期平移到安装当天附近；本案例保留 INSERT 里的原始日期，所以日期与在 Snowflake 里装出来的演示库不同，取值本身未改。
- 02：时间戳去掉了表示 UTC 的「Z」，表里的时间仍是 UTC。
- 04：UCI 页面原话称 AI4I 2020 是「a synthetic dataset that reflects real predictive maintenance data」；本案例又在它上面自建了设备与时间结构，因此归入虚构档。
- 07：原始数据说明没有写「闲置时间」的单位，本案例列名不加单位；「月内时段」是原始的 quarter 列（原说明为把一个月分成四段，29 日以后记作 Quarter5）。
- 06：Malloy 演示用的是 1966 年以来的全量召回，本案例只取 2021 年起的部分，所以数字与 Malloy 演示截图不同，度量口径相同。
- 10：thelook 的用户姓名、邮箱虽为虚构，本案例仍不带；Malloy 演示的销售额含已取消与已退货的订单明细，本案例题目沿用并在题干注明。
- 08：原始订单只有 2013-05-26 一天；仓库「停运」是题目里的假设情景，原始数据没有停运记录。运费费率表有 3 行完全重复，照原样保留。
