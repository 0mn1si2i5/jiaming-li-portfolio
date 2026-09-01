export const site = {
  name: 'Jiaming Li',
  description: 'Jiaming Li works across product development, research, and independent projects.',
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
    sideB: 'https://github.com/0mn1si2i5/Side-B',
    nbtiWebsite: 'https://0mn1si2i5.github.io/NBTI/',
    nbtiGithub: 'https://github.com/0mn1si2i5/NBTI',
    rsz: 'https://steamcommunity.com/sharedfiles/filedetails/?id=2804107924',
    dshHandoff: 'https://github.com/0mn1si2i5/dsh-handoff',
  },
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
    },
  ],
} as const;
