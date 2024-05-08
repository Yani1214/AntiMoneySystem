<template>
    <section>
      <!-- <ZySearchForm
          :formValue="state.query.params"
          @submit="goPage"
          @reset="handleReset"
      >
        <a-form-item name="operator">
          <a-input v-model="state.query.params.operator" allowClear
                   placeholder="请输入操作人" @pressEnter="goPage"
                   autocomplete="off"/>
        </a-form-item>
        <a-form-item name="module">
          <a-input v-model="state.query.params.missonNumber" allowClear
                   placeholder="请输入任务流水号" @pressEnter="goPage"
                   autocomplete="off"/>
        </a-form-item>
  
        <a-form-item name="operatorIP">
          <a-input v-model="state.query.params.bank" allowClear
                   placeholder="请输入交易表所属银行" @pressEnter="goPage"
                   autocomplete="off"/>
        </a-form-item>
      </ZySearchForm> -->
      
      <ZyFittleRow @add="goEdit"
                   @delete="goDeleteAll"
                   addAuth="sys:users_opt_logs:create"
                   deleteText="批量删除"
                   deleteAuth="sys:users_opt_logs:deleteAll"
      >
      
        <a-button type="primary" size="small" @click="goExport">
          <template #icon>
            <IconFont type="icon-daochu1"/>
          </template>
          导出
        </a-button>
        <a-upload
                :headers="headers"
                @change="handleImportChange"
                :showUploadList="false"
                action="/v1/process/byhand/import">
          <a-button type="primary" size="small">
            <template #icon>
              <IconFont type="icon-daoru1"/>
            </template>
            导入
          </a-button>
        </a-upload>
  
        <a-button type="primary" size="small" @click="getToDatabase">
          <template #icon>
            <IconFont type="icon-down-arrow"/>
          </template>
          核验完成，上传数据库
        </a-button>
      </ZyFittleRow>
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
      <!-- <ZyModal :minWidth="650" :show="state.show.edit" :title="state.editTitle" key="GetUsers_opt_logsInfo"
               @close="close">
        <GetUsers_opt_logsInfo :updateData="state.updateData" @close="close"/>
      </ZyModal>
      <ZyModal :minWidth="650" :show="state.show.view" title="查看操作日志" key="ViewUsers_opt_logsInfo"
               @close="close">
        <ViewUsers_opt_logsInfo :viewData="state.viewData" @close="close"/>
      </ZyModal> -->
    </section>
  
  </template>
  
  <script setup>
  /***操作日志管理 生成：2023/7/7 下午2:37:53***/
  /**
   * 操作权限：
   'sys:users_opt_logs:list'
   'sys:users_opt_logs:create'
   'sys:users_opt_logs:update'
   'sys:users_opt_logs:delete'
   'sys:users_opt_logs:deleteAll'
   */
  
  import {reactive, toRaw} from 'vue'
  // import GetUsers_opt_logsInfo from "./get-byhand-info.vue";
  // import ViewUsers_opt_logsInfo from "./view-byhand-info.vue";
  
  import ZyModal from "comps/common/ZyModal.vue";
  import ZyToolButton from "comps/common/ZyToolButton.vue";
  import ZyFittleRow from "comps/common/ZyFittleRow.vue";
  import ZySearchForm from "comps/common/ZySearchForm.vue";
  
  import {ZyConfirm, ZyNotification} from "libs/util.toast";
  import {isEmptyObject} from "libs/util.common";
  import {TimeUtils} from "libs/util.time";
  import {hasPerms} from 'libs/util.common';
  
  // import {
  //   users_opt_logsDelete,
  //   users_opt_logsExport,
  //   users_opt_logsList,
  //   users_opt_logsDeleteAll,
  //   users_opt_logsDownloadTemplate
  // } from "api/modules/api.users_opt_logs";

  import {
    processByhand,
    processExport,
    processDetect
  }from "api/modules/api.process";
  
  import dbUtils from "libs/util.strotage";
  const columns = [
    {title: "任务流水号", dataIndex: "missonNumber", key: "missonNumber", align: 'center'},
    {title: "交易表所属银行", dataIndex: "bank", key: "bank", align: 'center'},
    {title: "修改时间", dataIndex: "createdAt", key: "createdAt", align: 'center'},
    // {title: "操作人", dataIndex: "operator", key: "operator", align: 'center'},
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
    processByhand(p).then(res => {
      state.loading.spinning = false
      let datas = res.data
      for (const data of datas) {
        data.createdAt = TimeUtils.formatTime(data.createdAt)
        data.updatedAt = TimeUtils.formatTime(data.updatedAt)
      }
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


  // // 下载模板
  // const getTemplate =()=>{
  //   users_opt_logsDownloadTemplate().then(res => {
  //     state.loading.spinning = false
  //   }).catch(err => {
  //     state.loading.spinning = false
  //     console.log(err)
  //   })
  // }
  
  // // 批量删除
  // const goDeleteAll = () => {
  //   ZyConfirm('确认删除数据?').then(ok => {
  //     ok && users_opt_logsDeleteAll({ids: state.selectedRowKeys || []}).then(res => {
  //       ZyNotification.success('删除成功')
  //       goPage()
  //     })
  //   })
  // }
  // const goDelete = (row) => {
  //   ZyConfirm('确认删除该条数据?').then(ok => {
  //     ok && users_opt_logsDelete(row).then(res => {
  //       ZyNotification.success('删除成功')
  //       goPage()
  //     })
  //   })
  // }

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
  