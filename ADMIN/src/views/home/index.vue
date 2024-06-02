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
      <ZySectionHeader title="我们的产品" titleNum="01"/>
      <a-row justify="center" align="top" :gutter="16">
        <a-col>
          <a-card :bordered="true">
            <h4>WHO ARE WE？</h4>
            <br>
            <p>✨「No Escape」：一个致力于协助执法机构识别洗钱行为、实现追踪溯源的智能化系统。</p>
            <br>
            <p>✨「No Escape」旨在协助执法机关打击以网络赌博、电信诈骗为代表的网络空间洗钱犯罪行为，维护经济社会清明稳定，保护广大人民财产安全。</p>
            <br>
            <p>✨「No Escape」让洗钱行为有迹可循，让洗钱分子无处可逃。</p>
            <br>
          </a-card>
        </a-col>
        <a-col :span="12">
          <a-card :bordered="true">
            <h4>WHY CHOOSE US？</h4>
            <br>
            <p>✨选择「No Escape」选择“有效”：「No Escape」具有系统用户管理、交易数据分析、人员案例分析、涉案团伙分析和交易数据分布五大功能板块，为您提供全过程智能化反洗钱服务。</p>
            <br>
            <p>✨选择「No Escape」选择”高效“：「No Escape」模型集成深度学习与传统规则匹配算法，省去人工逐条核查，为您提供高效便捷的反洗钱服务。</p>
            <br>
            <p>✨选择「No Escape」选择“长效”：「No Escape」结合专家审核结果，对内置模型及时优化，实时更新，自动化适应新型洗钱方式，为您提供长效持久的反洗钱服务。</p>
            <br>
          </a-card>
        </a-col>
        <a-col :span="12">
          <a-card :bordered="true">
            <h4>WHAT CAN WE DO？</h4>
            <br>
            <p>✨「No Escape」集合深度学习模型与传统规则匹配模型，实现对复杂的金融交易网络进行高效分析，在提高洗钱行为检测效率的同时提供高度结果可解释性。</p>
            <br>
            <p>✨「No Escape」利用数据可视化、有向图分析等技术，支持对涉案资金流向进行追踪分析，实现对团伙洗钱行为的追踪溯源。</p>
            <br>
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
