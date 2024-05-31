<template>
  <section class="zy-container">
    <div class="img-box">
      <ZyLogo :showTitle="false" size="80"/>
    </div>
    <hr/>
    <section class="one">
      <header class="major">
        <h1>欢迎使用NoEscape！</h1>
        <p class="sub-title">请点击 "上传文件" 以批量上传需要检测的文件(zip格式)</p>
        <p>上传成功后，点击 "开始检测" 以进行数据分析</p>

        <!-- <a target="_blank" >
          <a-button type="primary" id="upload" @click="readyToUpdate">上传文件</a-button>
        </a> -->
        <ZyUpload @uploadChange="goPage(1)" />

        <a target="_blank">
          <a-button type="dashed" id="analysis" @click="goDetection">开始检测</a-button>
        </a>

      </header>
    </section>
    <section class="intro">
      <ZySectionHeader title="我们的项目" titleNum="01"/>
      <a-row justify="center" align="top" :gutter="16">
        <a-col>
          <a-card :bordered="true">
            <p>✨vue3-antd-plus在线文档：<a href="https://z568_568.gitee.io/vue3-antd-plus" target="_blank">https://z568_568.gitee.io/vue3-antd-plus</a>
            </p>
            <p>✨QQ交流群: 529675917</p>
            <p>✨作者邮箱：yizhou568@gmail.com</p>
          </a-card>
        </a-col>
        <a-col>
          <a-card :bordered="true">
            <p>✨vue3-antd-plus在线文档：<a href="https://z568_568.gitee.io/vue3-antd-plus" target="_blank">https://z568_568.gitee.io/vue3-antd-plus</a>
            </p>
            <p>✨QQ交流群: 529675917</p>
            <p>✨作者邮箱：yizhou568@gmail.com</p>
          </a-card>
        </a-col>
        <a-col>
          <a-card :bordered="true">
            <p>✨vue3-antd-plus在线文档：<a href="https://z568_568.gitee.io/vue3-antd-plus" target="_blank">https://z568_568.gitee.io/vue3-antd-plus</a>
            </p>
            <p>✨QQ交流群: 529675917</p>
            <p>✨作者邮箱：yizhou568@gmail.com</p>
          </a-card>
        </a-col>
        <a-col>
          <a-card :bordered="true">
            <p>✨vue3-antd-plus在线文档：<a href="https://z568_568.gitee.io/vue3-antd-plus" target="_blank">https://z568_568.gitee.io/vue3-antd-plus</a>
            </p>
            <p>✨QQ交流群: 529675917</p>
            <p>✨作者邮箱：yizhou568@gmail.com</p>
          </a-card>
        </a-col>
      </a-row>

      <ZySectionHeader title="关于我们" titleNum="02"/>
      <a-row justify="center" align="top" :gutter="16">
        <a-col>
          <a-card :bordered="true">
            <p>✨vue3-antd-plus在线文档：<a href="https://z568_568.gitee.io/vue3-antd-plus" target="_blank">https://z568_568.gitee.io/vue3-antd-plus</a>
            </p>
            <p>✨QQ交流群: 529675917</p>
            <p>✨作者邮箱：yizhou568@gmail.com</p>
          </a-card>
        </a-col>
      </a-row>
    </section>
  </section>
</template>

<script setup>
import {watchEffect, reactive, ref, toRaw} from 'vue'
import ZyLogo from "../../components/common/ZyLogo.vue";
import ZySectionHeader from "../../components/common/ZySectionHeader.vue";
import ZyUpload from "../../components/common/ZyUpload.vue";

import {
    analysisDetection,
  }from "api/modules/api.analysis";

import {ZyConfirm, ZyNotification} from "libs/util.toast";

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

const goDetection = () => {
  state.loading.spinning = true
  // 将响应式query返回起原始对象
  let p = toRaw(state.query)
  analysisDetection(p).then(res => {
    state.loading.spinning = false
    console.log(res)
    if(res.result == 'ok'){
      ZyNotification.success(res.message ||'请耐心等待')
    }
    if(res.result == 'no'){
      ZyNotification.error(res.message || '请重新进行检测')
    }
  }).catch(err => {
    state.loading.spinning = false
    console.log(err)
  })
};

</script>

<style lang="scss" scoped>
.img-box {
  width: 120px;
  height: auto;
  margin: 2rem auto 0;
}

.intro {
  max-width: 1200px;
  margin: 0 auto;

  .social-list {
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 2.5rem 0;

    .iconfont {
      font-size: 2rem;
      margin: 5px;
    }
  }

  .zs-list {
    display: flex;

    .zs {
      display: inline-block;
      width: 120px;
      margin: 1rem;
    }

  }
}

.one {
  max-width: 1200px;
  margin: 2rem auto;

  .major {
    text-align: center;
    margin-bottom: 2rem;

    h1 {
      margin-bottom: 1rem;
    }

    p:nth-child(3) {
      margin-bottom: 1rem;
    }

    a {
      margin: .5rem;
    }
  }
}
</style>
