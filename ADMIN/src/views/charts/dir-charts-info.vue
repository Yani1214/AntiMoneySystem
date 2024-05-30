<template>
    <section>
      <!-- 搜索框 -->
      <div class="search-bar">
        <a-row type="flex" justify="start" align="middle" :gutter="10">
          <a-col :span="18">
            <a-input v-model:value="searchValue" placeholder="请输入需要查询的人员名称" @pressEnter="search"></a-input>
          </a-col>
          <a-col :span="6">
            <a-button type="primary" size="middle" @click="search">查询</a-button>
          </a-col>
        </a-row>
      </div>
      
      <a-button type="primary" size="small" @click="key_point">
        <template #icon></template>
        返回查看涉案团伙交易数据分布情况
      </a-button>
      <br>
      <br>
      

      <!-- 饼状图 -->
      <div>
        <Piechart :searchValue="triggeredSearchValue" @searchResult="onSearchResult" :update="triggeredUpdateValue" @updateResult="onUpdate"/>
      </div>
      <br>
      <br>

      <div style="display: flex; flex: 1">
        <!-- 左侧折线图 -->
        <div class="left-panel">
          <Linechart :searchValue="triggeredSearchValue" @searchResult="onSearchResult" :update="triggeredUpdateValue" @updateResult="onUpdate"/>
        </div>
  
        <!-- 右侧柱状图 -->
        <div class="right-panel">
          <Barchart :searchValue="triggeredSearchValue" @searchResult="onSearchResult" :update="triggeredUpdateValue" @updateResult="onUpdate"/>
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
    import { ServerInfo } from 'neo4j-driver';

    const searchValue = ref(''); // 声明 searchValue
    const triggeredSearchValue = ref(''); // 声明 triggeredSearchValue
    const triggeredUpdateValue = ref('');
    
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
    // console.log(triggeredSearchValue.value)
    if (searchValue.value !== '') {
      triggeredSearchValue.value = searchValue.value;
      ZyNotification.success('查询已触发');
    } else {
      // 在这里编写 triggeredSearchValue 为空时的逻辑
      ZyNotification.warning('请输入有效的查询值');
    }
  }
  
  // 监听子组件的 searchResult 事件，处理搜索结果
  const onSearchResult = (Data) => {
    // 处理从子组件传递过来的柱状图数据
    console.log('接收到子组件传递的数据:', Data);
    ZyNotification.success('查询成功');
  };

  const key_point = () =>{
    triggeredUpdateValue.value = Date.now().toString();
    ZyNotification.success('正在返回');

  }

  // 监听子组件的 searchResult 事件，处理搜索结果
  const onUpdate = (Data) => {
    console.log(Data)
    if(Data !== '')
      // 处理从子组件传递过来的柱状图数据
      ZyNotification.success('返回成功');
  };
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
  