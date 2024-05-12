/**
 * 在主框架内显示
 * 路由配置说明
 * {
      path: '/dir-demo-info',    // 页面地址（唯一）
      name: 'dir-demo-info',     // 页面名称（唯一）
      hidden: false,              // 隐藏（不展示在侧边栏菜单）
      meta: {
          title: '用户管理',       // 页面标题
          icon: 'yonghuguanli',  // 页面图标
          cache: true,          // 页面是否进行缓存 默认true
          link: false,           // 页面是否是外链 默认false
          frameSrc: false,       // 页面是否是内嵌 默认false
          requiresAuth: false,   // 页面是否是需要登录 默认true
          perms: [               // 页面的操作的权限列表
              'sys:user:list',   // 查询
              'sys:user:create', // 增加
              'sys:user:update', // 更新
              'sys:user:delete', // 删除
          ],
      },
      component: () => import('@/views/sys/users/dir-users-info.vue'),// 懒加载页面组件
   }
 *
 */
   const frameIn = [
    {
        path: '/',
        redirect: {name: 'index'},
        component: () => import('@/layout/index.vue'),
        /*************************************************************************************/
        /********************children 建议最多 再加一级children  否则侧边栏体验不好*********************/
        /*************************************************************************************/
        children: [
            {
                path: '/index',
                name: 'index',
                meta: {
                    cache: true,
                    title: '首页',
                    icon: 'shouye',
                    requiresAuth: false,
                },
                component: () => import('@/views/home/index.vue'),
            },

            {
                path: '/dir-byhand-info.vue',
                name: 'dir-byhand-info.vue',
                meta: {
                    cache: true,
                    title: '人工数据处理',
                    requiresAuth: false,
                    icon: 'shujuzhongxinshujucangku'
                },
                component: () => import('@/views/byhand/dir-byhand-info.vue'),
            },
            {
                path: '/dir-person-info',
                name: 'dir-person-info',
                meta: {
                    cache: true,
                    title: '用户案例分析',
                    requiresAuth: false,
                    icon: 'yonghuming'
                },
                component: () => import('@/views/caseAnalysis/dir-person-info.vue'),
            },
            {
                path: '/dir-group-info',
                name: 'dir-group-info',
                meta: {
                    cache: true,
                    title: '洗钱团伙分析',
                    requiresAuth: false,
                    icon: 'zuzhi'
                },
                component: () => import('@/views/caseAnalysis/dir-group-info.vue'),
            },

            {
              path: '/dataCenter',
              name: 'dataCenter',
              meta: {
                  cache: true,
                  title: '交易数据分布',
                  requiresAuth: false,
                  icon: 'cengji'
              },
              component: () => import('@/views/demo/dataCenter/index.vue'),
          },

          {
              path: '/dataCenter',
              name: 'dataCenter',
              meta: {
                  cache: true,
                  icon: 'shujuzhongxin',
                  title: '数据大屏',
                  requiresAuth: false,
              },
              component: () => import('@/views/demo/dataCenter/index.vue'),
          },
  
        // 重定向页面 必须保留
        {
          path: "/redirect/:path(.*)/:_origin_params(.*)?",
          name: "Redirect",
          hidden: true, //不展示在侧边栏菜单
          meta: {
            title: "重定向"
          },
          component: () => import("@/views/sys/function/redirect")
        },
      ]
    },
  ]
  
  /**
   * 在主框架之外显示
   */
  const frameOut = [
    // 登录
    {
      path: "/login",
      name: "login",
      meta: {
        title: "登录"
      },
      component: () => import("@/views/sys/login/dir-login-info.vue")
    },
    {
      path: "/dataCenter",
      name: "dataCenter",
      meta: {
        title: "大屏展示"
      },
      component: () => import("@/views/demo/dataCenter/index.vue")
    }
  ];
  
  /**
   * 错误页面
   */
  const errorPage = [
    {
      path: "/401",
      name: "401",
      component: () => import("@/views/error/401.vue"),
      meta: {
        title: "401"
      }
    },
    {
      path: "/:pathMatch(.*)*",
      name: "404",
      component: () => import("@/views/error/404.vue"),
      meta: {
        title: "404"
      }
    }
  ];
  
  // 导出需要显示菜单的
  export const frameInRoutes = frameIn;
  
  // 重新组织后导出
  export default [...frameIn, ...frameOut, ...errorPage];
  