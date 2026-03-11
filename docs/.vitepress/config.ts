import { defineConfig } from 'vitepress'

export default defineConfig({
  title: '喜食AI',
  description: '把 B站做饭视频变成图文菜谱',
  base: '/xishi-recipes/',

  themeConfig: {
    logo: '/hero.png',
    nav: [
      { text: '首页', link: '/' },
      { text: '所有菜谱', link: '/recipes/' },
      { text: '使用方法', link: '/guide/' },
    ],

    sidebar: {
      '/guide/': [
        {
          text: '快速上手',
          items: [
            { text: '使用方法', link: '/guide/' },
          ]
        }
      ],
      '/recipes/': [
        {
          text: '所有菜谱',
          items: [
            { text: '金包银蛋炒饭', link: '/recipes/金包银or锅气蛋炒饭一个视频教你们成为蛋炒饭大王/' },
          ]
        }
      ]
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/XDcat/xishi-recipes' }
    ],

    footer: {
      message: '由 AI 生成，仅供参考',
      copyright: '© 2025 喜食AI'
    }
  }
})
