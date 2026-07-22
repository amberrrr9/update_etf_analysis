import type React from 'react';
import {
  AlertTriangle,
  ArrowUpRight,
  CalendarDays,
  Clock3,
  Database,
  ExternalLink,
  FileText,
  Landmark,
  LineChart,
  Newspaper,
  RefreshCw,
  ShieldCheck,
  Sparkles,
} from 'lucide-react';

type MarketIndex = {
  name: string;
  code: string;
  change: string;
  turnover: string;
  tone: 'up' | 'down' | 'flat';
};

type EvidenceItem = {
  label: string;
  value: string;
  note: string;
};

type ProductRow = {
  code: string;
  name: string;
  type: '场内 ETF' | '联接基金';
  shareClass?: string;
  target?: string;
  oneDay: string;
  oneWeek: string;
  threeMonths: string;
  oneYear: string;
  size: string;
  date: string;
};

type FocusIndustry = {
  name: string;
  navLabel: string;
  category: string;
  indexName: string;
  indexCode: string;
  summary: string;
  reason: string;
  evidence: EvidenceItem[];
  news: string[];
  risks: string[];
  products: ProductRow[];
};

type MarketOverview = {
  label: string;
  value: string;
  note: string;
};

const marketIndices: MarketIndex[] = [
  { name: '沪深300', code: '000300.SH', change: '+0.42%', turnover: '2,846 亿', tone: 'up' },
  { name: '中证500', code: '000905.SH', change: '-0.18%', turnover: '1,924 亿', tone: 'down' },
  { name: '创业板指', code: '399006.SZ', change: '+1.16%', turnover: '2,103 亿', tone: 'up' },
  { name: '科创50', code: '000688.SH', change: '+1.88%', turnover: '687 亿', tone: 'up' },
];

const marketOverview: MarketOverview[] = [
  { label: '上涨行业', value: '21 / 31', note: '行业扩散度偏积极' },
  { label: 'ETF 成交额', value: '1,186 亿', note: '较20日均值 +14%' },
  { label: '强势风格', value: '成长', note: '创业板、科创相对占优' },
  { label: '风险温度', value: '中性偏暖', note: '波动未显著放大' },
];

const focusIndustries: FocusIndustry[] = [
  {
    name: '半导体',
    navLabel: '半导体',
    category: '科技制造',
    indexName: '中证半导体产业指数',
    indexCode: 'H30184.CSI',
    reason: '相对强度、成交放大、成分股广度同时触发。',
    summary:
      '半导体方向今日表现强于主要宽基，近一周相对收益扩大，行业内部上涨扩散度较高；公开信息主要集中在设备国产化、AI 算力链需求和部分权重公司业绩预告。',
    evidence: [
      { label: '昨日收益', value: '+2.84%', note: '高于行业线索阈值' },
      { label: '近一周收益', value: '+6.12%', note: '相对沪深300 +4.7pct' },
      { label: '成交变化', value: '1.63x', note: '较近20日均值放大' },
      { label: '成分股广度', value: '72%', note: '上涨成分股占比' },
    ],
    news: ['设备端国产替代订单预期升温', 'AI 服务器链条带动先进封装关注度提升'],
    risks: ['短期成交放大后需观察持续性', '海外出口限制仍可能扰动板块估值'],
    products: [
      {
        code: '512480',
        name: '国联安中证全指半导体ETF',
        type: '场内 ETF',
        oneDay: '+2.61%',
        oneWeek: '+5.82%',
        threeMonths: '+11.40%',
        oneYear: '+18.35%',
        size: '216.4 亿',
        date: '2026-07-21',
      },
      {
        code: '007300',
        name: '国联安中证全指半导体ETF联接A',
        type: '联接基金',
        shareClass: 'A',
        target: '512480',
        oneDay: '+2.44%',
        oneWeek: '+5.41%',
        threeMonths: '+10.82%',
        oneYear: '+17.21%',
        size: '38.7 亿',
        date: '2026-07-21',
      },
    ],
  },
  {
    name: '创新药',
    navLabel: '创新药',
    category: '医药健康',
    indexName: '中证创新药产业指数',
    indexCode: '931152.CSI',
    reason: '一周维度趋势延续，成交温和放大，新闻证据密度较高。',
    summary:
      '创新药指数近一周维持相对强势，成交额温和放大，主要贡献来自头部 CXO 与创新药企；新闻证据集中于医保谈判预期、海外授权交易和临床进展。',
    evidence: [
      { label: '昨日收益', value: '+1.37%', note: '未单独触发阈值' },
      { label: '近一周收益', value: '+4.86%', note: '达到行业线索阈值' },
      { label: '成交变化', value: '1.28x', note: '温和放大' },
      { label: '成分股广度', value: '66%', note: '上涨成分股占比' },
    ],
    news: ['多家公司披露海外授权及临床阶段更新', '医保目录调整预期带来情绪修复'],
    risks: ['单个管线事件对指数权重股影响较大', '医保与集采政策预期仍需跟踪'],
    products: [
      {
        code: '159992',
        name: '银华中证创新药产业ETF',
        type: '场内 ETF',
        oneDay: '+1.22%',
        oneWeek: '+4.42%',
        threeMonths: '+8.06%',
        oneYear: '+9.74%',
        size: '84.1 亿',
        date: '2026-07-21',
      },
      {
        code: '012781',
        name: '银华中证创新药产业ETF发起式联接C',
        type: '联接基金',
        shareClass: 'C',
        target: '159992',
        oneDay: '+1.16%',
        oneWeek: '+4.18%',
        threeMonths: '+7.72%',
        oneYear: '+9.12%',
        size: '12.5 亿',
        date: '2026-07-21',
      },
    ],
  },
];

const toneClass = {
  up: 'text-rose-600',
  down: 'text-emerald-600',
  flat: 'text-secondary-text',
};

const recommendedIndustry = focusIndustries[0];

const EtfResearchPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="sticky top-0 z-20 border-b border-border/80 bg-card/95 backdrop-blur">
        <div className="mx-auto flex w-full max-w-[1480px] flex-col gap-3 px-4 py-3 sm:px-6 lg:px-8">
          <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
            <div className="flex min-w-0 items-center gap-3">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-[8px] bg-primary text-primary-foreground">
                <LineChart className="h-5 w-5" />
              </div>
              <div className="min-w-0">
                <div className="text-base font-semibold text-foreground">AI ETF Research</div>
                <div className="text-xs text-muted-text">Index-first daily market desk</div>
              </div>
            </div>
            <nav className="flex min-w-0 items-center gap-1 text-sm">
              <a href="#market" className="shrink-0 rounded-[6px] bg-primary px-3 py-2 font-medium text-primary-foreground">
                全市场
              </a>
            </nav>
          </div>

          <div className="flex flex-wrap items-center gap-2 text-xs text-secondary-text">
            <span className="inline-flex items-center gap-1.5 rounded-[6px] border border-border bg-background px-2.5 py-1">
              <CalendarDays className="h-4 w-4 text-primary" />
              2026-07-21
            </span>
            <span className="inline-flex items-center gap-1.5 rounded-[6px] border border-border bg-background px-2.5 py-1">
              <Clock3 className="h-4 w-4 text-amber-500" />
              数据更新 15:28
            </span>
            <span className="inline-flex items-center gap-1.5 rounded-[6px] border border-border bg-background px-2.5 py-1">
              <Database className="h-4 w-4 text-emerald-500" />
              样例数据
            </span>
          </div>
        </div>
      </div>

      <div className="mx-auto flex w-full max-w-[1480px] flex-col gap-5 px-4 py-5 sm:px-6 lg:px-8">
        <header id="market" className="flex scroll-mt-28 flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div className="min-w-0">
            <h1 className="text-2xl font-semibold tracking-normal text-foreground sm:text-3xl">
              全市场 ETF 研究首页
            </h1>
            <p className="mt-2 max-w-4xl text-sm leading-6 text-secondary-text">
              首页先观察市场环境、行业扩散、成交结构和风险温度，再进入具体行业。以下内容仅呈现公开数据与证据链，不构成投资建议。
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <button
              type="button"
              className="inline-flex h-10 items-center gap-2 rounded-[6px] border border-border bg-card px-3 text-sm font-medium text-secondary-text transition-colors hover:bg-hover hover:text-foreground"
            >
              <RefreshCw className="h-4 w-4" />
              刷新样例
            </button>
            <button
              type="button"
              className="inline-flex h-10 items-center gap-2 rounded-[6px] bg-primary px-3 text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90"
            >
              <FileText className="h-4 w-4" />
              查看日报
            </button>
          </div>
        </header>

        <main className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_360px]">
          <section className="flex min-w-0 flex-col gap-5">
            <section className="rounded-[8px] border border-border bg-card p-4 shadow-soft-card">
              <div className="mb-4 flex items-center justify-between gap-3">
                <div>
                  <h2 className="text-base font-semibold text-foreground">今日市场研究</h2>
                  <p className="mt-1 text-sm text-secondary-text">主要宽基、风格指数与成交概览</p>
                </div>
                <LineChart className="h-5 w-5 shrink-0 text-primary" />
              </div>
              <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
                {marketIndices.map((item) => (
                  <article key={item.code} className="rounded-[8px] border border-border/80 bg-background p-3">
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <h3 className="truncate text-sm font-medium text-foreground">{item.name}</h3>
                        <p className="mt-1 text-xs text-muted-text">{item.code}</p>
                      </div>
                      <span className={`text-sm font-semibold ${toneClass[item.tone]}`}>{item.change}</span>
                    </div>
                    <div className="mt-4 text-xs text-secondary-text">成交额</div>
                    <div className="mt-1 text-lg font-semibold text-foreground">{item.turnover}</div>
                  </article>
                ))}
              </div>
            </section>

            <section className="rounded-[8px] border border-border bg-card p-4 shadow-soft-card">
              <div className="mb-4 flex items-center justify-between gap-3">
                <div>
                  <h2 className="text-base font-semibold text-foreground">市场环境总览</h2>
                  <p className="mt-1 text-sm text-secondary-text">从全市场角度判断今天是否值得继续下钻行业</p>
                </div>
                <Sparkles className="h-5 w-5 shrink-0 text-primary" />
              </div>
              <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
                {marketOverview.map((item) => (
                  <article key={item.label} className="rounded-[8px] border border-border/80 bg-background p-3">
                    <div className="text-xs text-muted-text">{item.label}</div>
                    <div className="mt-1 text-lg font-semibold text-foreground">{item.value}</div>
                    <div className="mt-1 text-xs leading-5 text-secondary-text">{item.note}</div>
                  </article>
                ))}
              </div>
              <div className="mt-4 rounded-[8px] border border-border/80 bg-background p-3 text-sm leading-6 text-secondary-text">
                今日全市场不是单一指数推动：创业板与科创相对更强，行业上涨家数超过半数，ETF 成交额较近20日均值放大。
                因此首页优先提示可继续跟踪的行业线索，而不是给出买卖判断。
              </div>
            </section>

            <section className="flex flex-col gap-4">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <h2 className="text-base font-semibold text-foreground">行业入口</h2>
                  <p className="mt-1 text-sm text-secondary-text">从全市场页点击行业卡片进入具体证据链</p>
                </div>
                <ShieldCheck className="h-5 w-5 shrink-0 text-emerald-500" />
              </div>

              <div className="grid gap-3 md:grid-cols-2">
                {focusIndustries.map((industry) => (
                  <a
                    key={`${industry.indexCode}-entry`}
                    href={`#industry-${industry.navLabel}`}
                    className="group rounded-[8px] border border-border bg-card p-4 shadow-soft-card transition-colors hover:border-primary/50 hover:bg-hover"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="rounded-[6px] bg-primary/10 px-2.5 py-1 text-sm font-medium text-primary">
                            {industry.name}
                          </span>
                          <span className="rounded-[6px] border border-border bg-background px-2.5 py-1 text-xs text-secondary-text">
                            {industry.category}
                          </span>
                        </div>
                        <h3 className="mt-3 text-sm font-semibold text-foreground">{industry.indexName}</h3>
                        <p className="mt-2 line-clamp-2 text-sm leading-6 text-secondary-text">{industry.reason}</p>
                      </div>
                      <ArrowUpRight className="h-5 w-5 shrink-0 text-muted-text transition-colors group-hover:text-primary" />
                    </div>
                  </a>
                ))}
              </div>

              {focusIndustries.map((industry) => (
                <article
                  id={`industry-${industry.navLabel}`}
                  key={industry.indexCode}
                  className="scroll-mt-32 rounded-[8px] border border-border bg-card p-4 shadow-soft-card"
                >
                  <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                    <div className="min-w-0">
                      <div className="mb-2 flex flex-wrap items-center gap-2">
                        <span className="rounded-[6px] bg-primary/10 px-2.5 py-1 text-sm font-medium text-primary">
                          {industry.name}
                        </span>
                        <span className="rounded-[6px] border border-border bg-background px-2.5 py-1 text-xs text-secondary-text">
                          {industry.category}
                        </span>
                        <span className="text-sm text-secondary-text">
                          {industry.indexName} · {industry.indexCode}
                        </span>
                      </div>
                      <p className="max-w-4xl text-sm leading-6 text-secondary-text">{industry.summary}</p>
                    </div>
                    <button
                      type="button"
                      className="inline-flex h-9 shrink-0 items-center justify-center gap-2 rounded-[6px] border border-border bg-background px-3 text-sm text-secondary-text transition-colors hover:bg-hover hover:text-foreground"
                    >
                      <ExternalLink className="h-4 w-4" />
                      详情
                    </button>
                  </div>

                  <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
                    {industry.evidence.map((item) => (
                      <div key={`${industry.indexCode}-${item.label}`} className="rounded-[8px] border border-border/80 bg-background p-3">
                        <div className="text-xs text-muted-text">{item.label}</div>
                        <div className="mt-1 text-lg font-semibold text-foreground">{item.value}</div>
                        <div className="mt-1 text-xs leading-5 text-secondary-text">{item.note}</div>
                      </div>
                    ))}
                  </div>

                  <div className="mt-4 grid gap-4 lg:grid-cols-2">
                    <div className="rounded-[8px] border border-border/80 bg-background p-3">
                      <div className="mb-2 flex items-center gap-2 text-sm font-medium text-foreground">
                        <Newspaper className="h-4 w-4 text-primary" />
                        新闻与政策证据
                      </div>
                      <ul className="space-y-2 text-sm leading-6 text-secondary-text">
                        {industry.news.map((item) => (
                          <li key={item} className="flex gap-2">
                            <ArrowUpRight className="mt-1 h-4 w-4 shrink-0 text-primary" />
                            <span>{item}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div className="rounded-[8px] border border-border/80 bg-background p-3">
                      <div className="mb-2 flex items-center gap-2 text-sm font-medium text-foreground">
                        <AlertTriangle className="h-4 w-4 text-amber-500" />
                        风险与观察变量
                      </div>
                      <ul className="space-y-2 text-sm leading-6 text-secondary-text">
                        {industry.risks.map((item) => (
                          <li key={item} className="flex gap-2">
                            <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                            <span>{item}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  <div className="mt-4 overflow-hidden rounded-[8px] border border-border/80">
                    <div className="flex items-center gap-2 border-b border-border/80 bg-background px-3 py-2 text-sm font-medium text-foreground">
                      <Landmark className="h-4 w-4 text-primary" />
                      对应基金产品
                    </div>
                    <div className="overflow-x-auto">
                      <table className="min-w-[860px] w-full text-left text-sm">
                        <thead className="bg-muted/60 text-xs text-secondary-text">
                          <tr>
                            <th className="px-3 py-2 font-medium">代码</th>
                            <th className="px-3 py-2 font-medium">名称</th>
                            <th className="px-3 py-2 font-medium">类型</th>
                            <th className="px-3 py-2 font-medium">昨日</th>
                            <th className="px-3 py-2 font-medium">近一周</th>
                            <th className="px-3 py-2 font-medium">近三个月</th>
                            <th className="px-3 py-2 font-medium">近一年</th>
                            <th className="px-3 py-2 font-medium">规模</th>
                            <th className="px-3 py-2 font-medium">日期</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-border/70">
                          {industry.products.map((product) => (
                            <tr key={product.code} className="bg-card">
                              <td className="px-3 py-3 font-medium text-foreground">{product.code}</td>
                              <td className="px-3 py-3 text-secondary-text">
                                {product.name}
                                {product.target ? (
                                  <span className="ml-2 text-xs text-muted-text">目标 ETF {product.target}</span>
                                ) : null}
                              </td>
                              <td className="px-3 py-3 text-secondary-text">
                                {product.type}{product.shareClass ? ` · ${product.shareClass}` : ''}
                              </td>
                              <td className="px-3 py-3 text-rose-600">{product.oneDay}</td>
                              <td className="px-3 py-3 text-rose-600">{product.oneWeek}</td>
                              <td className="px-3 py-3 text-rose-600">{product.threeMonths}</td>
                              <td className="px-3 py-3 text-rose-600">{product.oneYear}</td>
                              <td className="px-3 py-3 text-secondary-text">{product.size}</td>
                              <td className="px-3 py-3 text-muted-text">{product.date}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </article>
              ))}
            </section>
          </section>

          <aside className="flex flex-col gap-5">
            <section className="rounded-[8px] border border-primary/30 bg-card p-4 shadow-soft-card">
              <div className="flex items-start gap-3">
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-[8px] bg-primary/10 text-primary">
                  <Sparkles className="h-5 w-5" />
                </div>
                <div className="min-w-0">
                  <h2 className="text-base font-semibold text-foreground">推荐关注行业</h2>
                  <p className="mt-1 text-sm leading-6 text-secondary-text">
                    {recommendedIndustry.name} · {recommendedIndustry.indexName}
                  </p>
                </div>
              </div>
              <div className="mt-4 rounded-[8px] border border-border/80 bg-background p-3">
                <div className="text-sm font-medium text-foreground">{recommendedIndustry.reason}</div>
                <p className="mt-2 text-sm leading-6 text-secondary-text">{recommendedIndustry.summary}</p>
              </div>
              <div className="mt-3 grid gap-2">
                {recommendedIndustry.evidence.slice(0, 3).map((item) => (
                  <div key={item.label} className="flex items-center justify-between gap-3 rounded-[6px] bg-background px-3 py-2 text-sm">
                    <span className="text-secondary-text">{item.label}</span>
                    <span className="font-semibold text-foreground">{item.value}</span>
                  </div>
                ))}
              </div>
              <a
                href={`#industry-${recommendedIndustry.navLabel}`}
                className="mt-4 inline-flex h-9 w-full items-center justify-center gap-2 rounded-[6px] bg-primary text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90"
              >
                查看行业证据
                <ArrowUpRight className="h-4 w-4" />
              </a>
            </section>

            <section className="rounded-[8px] border border-border bg-card p-4 shadow-soft-card">
              <h2 className="text-base font-semibold text-foreground">日报状态</h2>
              <div className="mt-4 space-y-3">
                {[
                  ['交易日校验', '已完成'],
                  ['行情数据', '样例载入'],
                  ['行业线索', '2 个'],
                  ['微信摘要', '待生成'],
                ].map(([label, value]) => (
                  <div key={label} className="flex items-center justify-between gap-3 rounded-[8px] border border-border/70 bg-background px-3 py-2 text-sm">
                    <span className="text-secondary-text">{label}</span>
                    <span className="font-medium text-foreground">{value}</span>
                  </div>
                ))}
              </div>
            </section>

            <section className="rounded-[8px] border border-border bg-card p-4 shadow-soft-card">
              <h2 className="text-base font-semibold text-foreground">微信摘要预览</h2>
              <div className="mt-3 rounded-[8px] border border-border/80 bg-background p-3 text-sm leading-6 text-secondary-text">
                <p className="font-medium text-foreground">2026-07-21 ETF 每日研究</p>
                <p className="mt-2">成长风格强于宽基，半导体与创新药出现较明确的行业证据链。</p>
                <p className="mt-2">完整报告链接将在网站发布后生成。</p>
              </div>
            </section>

            <section className="rounded-[8px] border border-amber-300/60 bg-amber-50/70 p-4 text-amber-950 shadow-soft-card dark:border-amber-400/30 dark:bg-amber-400/10 dark:text-amber-100">
              <div className="flex gap-3">
                <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" />
                <div className="text-sm leading-6">
                  <h2 className="font-semibold">风险提示</h2>
                  <p className="mt-1">
                    页面数据为前端框架样例。正式版本需展示真实数据来源、数据日期、计算区间和新闻链接。
                  </p>
                </div>
              </div>
            </section>
          </aside>
        </main>
      </div>
    </div>
  );
};

export default EtfResearchPage;
