import { defineConfig } from 'vitepress'

export default defineConfig({
  title: '喜食AI',
  description: '从视频到菜谱，AI 帮你记录每一道美味',
  lang: 'zh-CN',
  base: '/xishi-recipes/',

  head: [
    ['link', { rel: 'icon', href: '/favicon.ico' }],
    ['meta', { name: 'theme-color', content: '#ff6b35' }],
  ],

  themeConfig: {
    logo: '🍳',
    siteTitle: '喜食AI',

    nav: [
      { text: '首页', link: '/' },
      { text: '菜谱', link: '/recipes/' },
    ],

    sidebar: {
      '/recipes/': [
        {
          text: '所有菜谱',
          items: [
            // 自动生成的菜谱会插入这里
          ],
        },
      ],
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/XDcat/xishi-recipes' },
    ],

    footer: {
      message: '用 AI 把每个做饭视频变成精美菜谱',
      copyright: '© 2025 喜食AI',
    },

    search: {
      provider: 'local',
    },
  },
})
