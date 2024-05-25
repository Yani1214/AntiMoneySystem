<template>
    <section>   
      <a-table
          bordered
          :resizable="true"
          :loading="state.loading"
          :columns="columns"
          :row-key="record => record._id"
          :pagination="state.query.pagination"
          @change="handleTableChange"
          :row-class-name="(_record, index) => (index % 2 === 1 ? 'table-striped' : null)"
          :data-source="state.dataList">
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'avatar'">
            <a-image
                :width="40"
                :src="record.avatar"
            />
          </template>
          <template v-else-if="column.key === 'action'">
            <ZyToolButton
                viewAuth="sys:users_opt_logs:list"
                editAuth="sys:users_opt_logs:update"
                deleteAuth="sys:users_opt_logs:delete"
                @view="goView(record)"
                @edit="goEdit(record)"
                @delete="goDelete(record)"
            >
            </ZyToolButton>
          </template>
        </template>  
      </a-table>

    </section>
  
  </template>
  
  <script setup>
  
  import {reactive, toRaw} from 'vue'
  import ZyToolButton from "comps/common/ZyToolButton.vue";
  import {ZyConfirm, ZyNotification} from "libs/util.toast";
  import {isEmptyObject} from "libs/util.common";
  import { analysisTrace }from "api/modules/api.analysis";
  import dbUtils from "libs/util.strotage";

  const columns = [
    {title: "嫌疑人姓名", dataIndex: "name", key: "name", align: 'center'},
    {title: "嫌疑人卡号", dataIndex: "card", key: "card", align: 'center'},
    {title: "关键度（综合度）", dataIndex: "keypoint", key: "keypoint", align: 'center'},
  ];
  const headers = {
    authorization: dbUtils.get('token')
  }
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
        columnKey: "keypoint",
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
  
  // 查询
  const goPage = (num = 1) => {
    state.query.pagination.current = num;
    getDataList()
  }
  // 重置查询条件
  const handleReset = () => {
    goPage()
  }
  // 分页
  const pageChange = ({current, pageSize}) => {
    // 更新当前页码和每页条数
    state.query.pagination = reactive({
      current: current,
      pageSize: pageSize,
    });
    getDataList()
  }
  // 排序
  const sorterChange = ({columnKey, order}) => {
    // 更新排序
    state.query.sort = reactive({
      current: columnKey,
      order: order,
    });
    getDataList()
  }
  
  // 加载数据
  const getDataList = () => {
    state.loading.spinning = true
    // 将响应式query返回起原始对象
    let p = toRaw(state.query)
    analysisTrace(p).then(res => {
      state.loading.spinning = false
      let datas = res.group
      state.dataList = datas
      state.query.pagination.total = res.data.total
      state.query.pagination.current = res.data.current
      state.query.pagination.pageSize = res.data.pageSize
    }).catch(err => {
      state.loading.spinning = false
      console.log(err)
    })
  
  }

  const onSelectChange = selectedRowKeys => {
    console.log(selectedRowKeys)
    state.selectedRowKeys = selectedRowKeys;
  };
  // 处理表格变化事件
  const handleTableChange = (paginationValue, filters, sorter) => {
    if (!isEmptyObject(paginationValue)) {
      pageChange(paginationValue)
    }
    if (!isEmptyObject(sorter)) {
      sorterChange(sorter)
    }
  };
  
  
  const goView = (row) => {
    state.show.view = true
    state.viewData = row
  }
  
  
  const goEdit = (row) => {
    state.show.edit = true
    row && row._id ? state.editTitle = '修改操作日志' : state.editTitle = '添加操作日志'
    state.updateData = row
  }

// 导出 ZIP 文件
const goExport = () => {
    state.loading.spinning = true;
    let p = toRaw(state.query)
    // 发送 POST 请求到后端的导出路由
    processExport(p).then(response => {
        state.loading.spinning = false;
        // console.log(response)
        // 创建一个 Blob 对象并保存 ZIP 文件数据
        const blob = new Blob([response], { type: 'application/zip',responseType: 'blob' });
        // 创建一个链接并设置下载属性，将 ZIP 文件链接到该链接上
        const link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = 'manual.zip'; // 设置下载的文件名
        // 模拟点击链接以触发下载
        link.click();
        // 释放 URL 对象
        window.URL.revokeObjectURL(link.href);
    }).catch(error => {
        state.loading.spinning = false;
        console.error('导出失败:', error);
        // 处理导出失败的情况
    });
}


  // 导入数据
  const handleImportChange = ({
                          file,
                        }) => {
    if (file.status === 'error') {
      ZyNotification.error(file.response.message || '导入失败')
    }
    if (file.status === 'done') {
      ZyNotification.success(file.response.message||'上传成功')
      goPage()
    }
  };

  // 导入到数据库
  const getToDatabase = () => {
    state.loading.spinning = true
    // 将响应式query返回起原始对象
    let p = toRaw(state.query)
    processDetect(p).then(res => {
      state.loading.spinning = false
      console.log(res)
      if(res.result == 'ok'){
        ZyNotification.success(res.message ||'已成功导入数据库')
      }
      if(res.result == 'no'){
        ZyNotification.error(res.message || '导入失败')
      }
    }).catch(err => {
      state.loading.spinning = false
      console.log(err)
    })
  };

  const close = (isSave) => {
    state.show.reset = false
    state.show.view = false
    state.show.edit = false
    isSave && goPage()
  }
  
  goPage()
  
  </script>
  
  <style scoped>
  
  </style>
  