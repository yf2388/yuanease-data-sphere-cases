# Yuanease Data Sphere 案例库

**Yuanease Data Sphere（数据星球）** 是 Yuanease 桌面应用里「实体模型」功能的技术品牌：把企业散落在 Excel、CSV 和数据库里的表格，整理成统一的业务实体、关系与指标，让数字员工按同一套口径回答业务问题。

本仓库收录 10 个可以从零复现的行业案例。每个案例都包含：

- `data/`：用 CSV 文件模拟一个业务数据库，体积在几 MB 以内；
- `README.md`：从新建资料库、上传表格、构筑实体模型、审核发布到问数的逐步教程，配 Yuanease 实拍截图；
- `gold.yaml`：实体、唯一标识列、关系与指标的金标，有主外键的数据集直接从原始建表语句推导；
- `questions.yaml`：10–16 道问答题，标准答案由题目里的 SQL 在 `data/` 上独立算出；每题的 `source` 写明出处：出自竞品或开源项目公开教程、示例查询的题（「原作者题」），或案例作者按数据补出的题（「自补题」）；
- `prepare/`：从原始公开数据（或固定随机数种子）重新生成 `data/` 的脚本。

## 案例一览

| 编号 | 案例 | 行业场景 | 数据来源 | 表数 |
|---|---|---|---|---|
| 01 | [多工厂供应链：库存、物料清单与订单](cases/01-supply-chain-network/) | 离散制造 · 供应链 | Snowflake 公开教程数据（MIT） | 11 |
| 02 | [冷链门店本体：库存、冷柜遥测与货运](cases/02-cold-chain-ontology/) | 冷链 · 设备遥测 | Microsoft Fabric 本体教程数据（MIT） | 7 |
| 03 | [自行车生产：物料清单、工单与工序](cases/03-bike-production-bom/) | 离散制造 · 生产执行 | Microsoft AdventureWorks（MIT） | 11 |
| 04 | [数控设备故障分析](cases/04-cnc-machine-failure/) | 机加工 · 设备维修 | UCI AI4I 2020（CC BY 4.0）+ 自建台账 | 6 |
| 05 | [采购与供应商指标](cases/05-purchasing-metrics/) | 采购 · 来料检验 | Microsoft AdventureWorks（MIT） | 9 |
| 06 | [整车质量分析](cases/06-auto-quality-analysis/) | 汽车 · 售后质量 | 自建合成数据 | 8 |
| 07 | [多工厂设备综合效率（OEE）](cases/07-multi-plant-oee/) | 注塑 / 冲压 / 装配 | 自建合成数据 | 7 |
| 08 | [配送中心停运后的订单影响与调拨](cases/08-supply-disruption/) | 泵阀制造 · 供应中断 | 自建合成数据 | 8 |
| 09 | [钢铁厂能耗分析](cases/09-steel-plant-energy/) | 钢铁 · 能源管理 | UCI 钢铁厂能耗数据（CC BY 4.0） | 4 |
| 10 | [定制加工订单的五类指标](cases/10-order-metric-types/) | 机加工 · 订单交付 | 自建合成数据 | 5 |

源自其他厂商公开教程的案例，只复现其业务场景与问题清单，并在案例 README 开头注明出处；教程文字与截图均为本仓库自行撰写与拍摄。

## 怎么用

1. 安装并登录 Yuanease 桌面应用（0.8.7 或更高版本）。
2. 克隆本仓库，或下载 ZIP 后解压。
3. 打开任意案例目录，按 `README.md` 的步骤操作；每个案例约 20–30 分钟。
4. 用下面的命令核对标准答案（需要 Python 3.9+ 与 PyYAML）：

```bash
python3 -I tools/casekit.py answers cases/01-supply-chain-network --check
```

## 评测口径

- **首扫加权准确率**：上传表格后点一次「构筑实体模型」，中途员工提问一律回答「不知道，请你按数据自己判断。」，把得到的实体模型与 `gold.yaml` 比对。实体、唯一标识列、关系、指标四项分别计算 F1，按 0.3 / 0.2 / 0.3 / 0.2 加权。
- **问答准确率**：模型审核发布后，逐题提问；回答中包含标准答案的全部取值（数字允许 0.5% 相对误差）判为正确。主指标只算原作者题，自补题单独报告；题库在实跑前冻结，`BANK.md` 记录每个 questions.yaml 的 sha256。
- **独立复现**：由没有参与制作的智能体，只拿到本仓库与 Yuanease 安装包，照 README 从零完成全部步骤。

各案例的实测成绩见对应 README 的「实测记录」。

### 实测汇总（2026-10-21，Yuanease Dev 0.8.7）

| 指标 | 结果 |
|---|---|
| 首扫加权准确率中位数 | 0.824（10 个案例；01–06 用 qwen3.8-max，中位数 0.824；07–10 用 deepseek-v4.1-flash，中位数 0.832） |
| 问答准确率（只算原作者题） | 52/55 = 94.5%，Wilson 95% 区间 0.85–0.98（55 题来自 8 个案例；06、09 的原始来源没有可回答的问题） |
| 问答准确率（案例作者补的题，单独报） | 82/86 = 95.3% |
| 独立复现 | 10/10 成功，每个案例 19–32 分钟 |

实体、唯一标识列、关系三项在多数案例接近满分；扣分主要在指标：员工目前多半只起草计数类指标，合计、比率类指标要在第 4 步说明口径或审核后补。

## 目录结构

```
cases/<编号-名称>/
  README.md        逐步教程与实测记录
  data/            案例数据（上传这里的全部文件）
  gold.yaml        实体模型金标
  questions.yaml   问答题、计算 SQL 与标准答案
  images/          教程截图
  prepare/         数据生成脚本
tools/casekit.py   核对标准答案、核验金标、给回答打分
tools/test_casekit.py  判分规则自检（标准答案必须判对、改错数字必须判错）
```

## 许可

代码采用 MIT 许可；教程、截图、金标、问答题与自建合成数据采用 CC BY 4.0；改编自第三方的数据按各自原始许可证使用，见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。完整说明见 [LICENSE](LICENSE)。

---

## English summary

**Yuanease Data Sphere** turns scattered spreadsheets and database tables into a governed entity model (entities, keys, relationships, metrics) that AI workers use to answer business questions consistently. This repository contains 10 reproducible manufacturing and supply-chain cases. Each case ships CSV data, a step-by-step tutorial with screenshots of the Yuanease desktop app, a gold-standard entity model derived from the source schema, and 10–16 questions whose answers are computed independently with SQL (`tools/casekit.py`); questions taken from the original vendor or open-source tutorials are reported separately from questions written for this repository. Cases derived from other vendors' public tutorials reproduce only the business scenario and question list; all text and screenshots are original. Code is MIT; tutorials, gold files and synthetic data are CC BY 4.0; third-party data keeps its original license (see THIRD_PARTY_NOTICES.md).
