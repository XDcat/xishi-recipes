import { defineConfig } from 'vitepress'

export default defineConfig({
  title: '喜食AI',
  description: '把 B站做饭视频变成图文菜谱',
  base: '/xishi-recipes/',

  themeConfig: {
    logo: '/hero.png',
    nav: [
      { text: '首页', link: '/' },
      {
        text: '所有菜谱',
        items: [
          { text: '糖醋排骨', link: '/recipes/隋卞一做_糖醋排骨_特厨做法/' },
          { text: '黄焖土鸡', link: '/recipes/厨师长教你_黄焖土鸡_的家常做法_味道很赞先收藏了/' },
          { text: '蛋炒饭两吃——金包银 & 狂野锅气版', link: '/recipes/金包银or锅气蛋炒饭一个视频教你们成为蛋炒饭大王/' },
          { text: '山东炒鸡', link: '/recipes/山东炒鸡的灵魂全在这勺酱里_生炒是关键_咸香打底_辣味点睛_这味道_一个字_绝/' },
        ]
      },
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
            { text: '糖醋排骨', link: '/recipes/隋卞一做_糖醋排骨_特厨做法/' },
            { text: '黄焖土鸡', link: '/recipes/厨师长教你_黄焖土鸡_的家常做法_味道很赞先收藏了/' },
            { text: '蛋炒饭两吃——金包银 & 狂野锅气版', link: '/recipes/金包银or锅气蛋炒饭一个视频教你们成为蛋炒饭大王/' },
            { text: '山东炒鸡', link: '/recipes/山东炒鸡的灵魂全在这勺酱里_生炒是关键_咸香打底_辣味点睛_这味道_一个字_绝/' },
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
