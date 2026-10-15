export const site = {
  name: 'Jiaming Li',
  description: 'Jiaming Li builds AI tools, interactive products, and research prototypes.',
  emails: [
    {
      id: 'personal',
      label: { en: 'Personal email', zh: '个人邮箱' },
      address: 'nomisomnis@gmail.com',
    },
    {
      id: 'school',
      label: { en: 'University email', zh: '学校邮箱' },
      address: 'E1442419@u.nus.edu',
    },
  ],
  resumePath: 'resume/jiaming-li-resume-zh.pdf',
  github: 'https://github.com/0mn1si2i5',
  links: {
    dialogTreeDemo: 'https://chat.golir.top/',
    dialogTreePaper: 'https://doi.org/10.1145/3772363.3798792',
    mundusWebsite: 'https://0mn1si2i5.github.io/Mundus/',
    mundusGithub: 'https://github.com/0mn1si2i5/Mundus',
    nbtiWebsite: 'https://0mn1si2i5.github.io/NBTI/',
    nbtiGithub: 'https://github.com/0mn1si2i5/NBTI',
    perchGithub: 'https://github.com/0mn1si2i5/perch',
    perchReleases: 'https://github.com/0mn1si2i5/perch/releases',
    rsz: 'https://steamcommunity.com/sharedfiles/filedetails/?id=2804107924',
    dshHandoff: 'https://github.com/0mn1si2i5/dsh-handoff',
  },
  now: {
    en: 'AI Technical Design Intern at Hupo Games',
    zh: 'Hupo Games AI 技术策划实习生',
  },
  experience: [
    {
      id: 'hupo-games',
      period: { en: 'Sep 2026 – present', zh: '2026.09 至今' },
      org: { en: 'Hupo Games', zh: 'Hupo Games' },
      role: { en: 'AI Technical Design Intern', zh: 'AI 技术策划实习生' },
      summary: {
        en: 'I help build the company’s internal production platform and AI tools that speed up everyday production work.',
        zh: '参与搭建公司内部生产平台，开发 AI 提效工具。',
      },
    },
    {
      id: 'bytedance',
      period: { en: 'May – Aug 2026', zh: '2026.05 – 2026.08' },
      org: { en: 'ByteDance · AI Data & Security', zh: '字节跳动 · AI 数据与安全' },
      role: { en: 'Speech Data Intern', zh: '语音数据实习生' },
      summary: {
        en: 'I led an iteration of the primary speech evaluation set, and independently designed and built a speech-data production tool.',
        zh: '负责主力语音评测集的迭代，并独立设计和开发一套语音数据生产工具。',
      },
      link: {
        label: { en: 'Read the case study', zh: '查看案例' },
        project: 'bytedance-ai-data',
      },
    },
    {
      id: 'ai4sg-lab',
      period: { en: 'Since 2025', zh: '2025 年起' },
      org: { en: 'AI4SG Lab, National University of Singapore', zh: '新加坡国立大学 AI4SG Lab' },
      role: { en: 'Human–AI collaboration and generative-AI creation', zh: '人机协作与生成式 AI 创作' },
      summary: {
        en: 'I study interfaces for long LLM conversations. Our tree-structured interface, Branchat, was presented as an ACM CHI 2026 Poster.',
        zh: '研究 LLM 长对话的交互界面，树状对话界面 Branchat 发表为 ACM CHI 2026 海报论文。',
      },
      link: {
        label: { en: 'Read the poster paper', zh: '阅读海报论文' },
        href: 'https://doi.org/10.1145/3772363.3798792',
      },
    },
  ],
  externalWork: [
    {
      id: 'dsh-handoff',
      year: { en: 'Aug 2026', zh: '2026 年 8 月' },
      kind: { en: 'DeepSeek Harness plugin', zh: 'DeepSeek Harness 插件' },
      title: { en: 'dsh-handoff', zh: 'dsh-handoff' },
      summary: {
        en: 'After joining the early developer beta, I built dsh-handoff to save and restore redacted, Git-aware context between DeepSeek Harness sessions.',
        zh: '作为 DeepSeek Harness 早期内测开发者，我开发了跨会话交接插件 dsh-handoff：在会话之间保存并恢复经过脱敏、带 Git 状态的交接记录。',
      },
      href: 'https://github.com/0mn1si2i5/dsh-handoff',
      linkLabel: { en: 'View on GitHub', zh: '在 GitHub 查看' },
    },
    {
      id: 'rsz-namelist',
      year: { en: 'May 2022', zh: '2022 年 5 月' },
      kind: { en: 'Community mod', zh: '社区模组' },
      title: { en: 'RSZ Namelist', zh: 'RSZ Namelist' },
      summary: {
        en: 'A Chinese naming mod for Stellaris that gives ships, planets, and leaders default names that read naturally in Chinese.',
        zh: '为《群星》提供更符合中文语境的舰船、星球与人物默认名称，改善中文玩家的沉浸体验。',
      },
      outcome: { en: '4,600+ current Steam Workshop subscribers', zh: '4,600+ 名 Steam 创意工坊订阅用户' },
      href: 'https://steamcommunity.com/sharedfiles/filedetails/?id=2804107924',
      linkLabel: { en: 'Visit Steam Workshop', zh: '前往 Steam 创意工坊' },
    },
  ],
} as const;
