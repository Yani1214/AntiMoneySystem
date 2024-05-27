<template>
    <section style="display: flex; flex-direction: column; height: 100%">
      <!-- 搜索框 -->
      <div class="search-bar">
        <a-row type="flex" justify="start" align="middle" :gutter="10">
          <a-col :span="18">
            <a-input v-model:value="searchValue" placeholder="请输入需要查询的用户名称" @pressEnter="search"></a-input>
          </a-col>
          <a-col :span="6">
            <a-button type="primary" size="middle" @click="search">查询</a-button>
          </a-col>
        </a-row>
      </div>
      <br>
      <br>

      <!-- 饼状图 -->
      <div>
        <Piechart/>
      </div>
      <br>
      <br>

      <div style="display: flex; flex: 1">
        <!-- 左侧折线图 -->
        <div class="left-panel">
          <Linechart/>
        </div>
  
        <!-- 右侧柱状图 -->
        <div class="right-panel">
          <Barchart/>
        </div>

      </div>
    </section>
  </template>
  
  <script setup>
    import echarts from 'echarts';
    import { reactive, ref, toRaw } from 'vue';
    import { ZyNotification } from 'libs/util.toast';
    import { chartsPerson } from 'api/modules/api.charts';
    import Barchart from './Barchart.vue';
    import Linechart from './Linechart.vue';
    import Piechart from './Piechart.vue';

    const state = reactive({
    show: {
      add: false,
      edit: false,
      view: false
    },
    editTitle: '编辑',
    activeComponent: null,
    // 暂存更新数据
    updateData: {},
    resetData: {},
    // 暂存查看数据
    viewData: {},
    selectedRowKeys: [],
    // 请求参数
    query: {
      params: {},
      pagination: {
        current: 1,
        pageSize: 11,
        total: 0,
        hideOnSinglePage: true,
      },
      sort: {
        columnKey: "createdAt",
        order: "descend" //降序（新的在前面）
      }
    },
    dataList: [],
    // loading
    loading: {
      spinning: false,
      tip: '加载中'
    }
  })


  const search = () =>{
    state.loading.spinning = true
    // 将响应式query返回起原始对象
    let p = toRaw(state.query)
    chartsPerson(p).then(res => {
      state.loading.spinning = false
      console.log(res)
      if(res.result == 'ok'){
        ZyNotification.success(res.message ||'已成功查询')
      }
      if(res.result == 'no'){
        ZyNotification.error(res.message || '查询失败')
      }
    }).catch(err => {
      state.loading.spinning = false
      console.log(err)
    })
  }

  </script>
  
  <style lang="less" scoped>
    .left-panel {
      flex: 1 1 50%; /* 左侧面板占三分之一 */
      max-width: 50%;
      box-sizing: border-box;
      padding-right: 10px;
    }
  
    .right-panel {
      flex: 1 1 50%; /* 右侧面板占三分之二 */
      max-width: 50%;
      box-sizing: border-box;
      padding-left: 10px;
    }
  </style>
  