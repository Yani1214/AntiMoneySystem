<template>
    <!-- 为 ECharts 准备一个具备大小（宽高）的 DOM -->
    <div id="chartLine" class="line-wrap"></div>
</template>

<script>
    import * as echarts from 'echarts';
    import 'echarts/theme/shine';//引入主题
    import {reactive, toRaw, markRaw} from 'vue';
    import { chartsGroup,chartsPerson } from 'api/modules/api.charts';

export default {
    name: 'Linechart',
    props: {
    searchValue: String,
    update: String
  },
    setup(){
    const state = reactive({
    show: {
      add: false,
      edit: false,
      view: false
    },
    editTitle: '编辑',
    activeComponent: null,
    updateData: {},
    resetData: {},
    viewData: {},
    selectedRowKeys: [],
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
      loading: {
        spinning: false,
        tip: '加载中'
      }
    });
      return { state };
  },
    data() {
      return {
        chartLine: null
      }
    },
    mounted() {
      // 监听 searchValue 变化，触发 getPerson 事件
      this.$watch(() => this.$props.searchValue, (newValue, oldValue) => {
        if (newValue !== oldValue) {
          this.getPerson(newValue);
        }
      });
      this.$watch(() => this.$props.update, (newValue, oldValue) => {
      if (newValue !== oldValue) {
        this.getGroup();
      }
    });
      this.$nextTick(() => {
        this.getGroup();
      })
    },
    methods: {
    formatLineData(data) {
      return data.map(item => {
        return { value: item.count, name: item.name };
      });
    },
      drawLineChart() {
        const formattedData = this.formatLineData(this.lineData);
        this.chartLine = markRaw(echarts.init(document.getElementById('chartLine'),'shine'));// 基于准备好的dom，初始化echarts实例
        let option = {
            title: {
                text: '交易时间段对应交易条数', // 设置折线图标题
                subtext: '以2021年为例', // 设置折线图副标题，可选
                left: 'center' // 标题居中对齐，可选
            },
            tooltip : {
                trigger: 'axis'
            },
            legend: {
                data: formattedData.map(item => item.name), 
                top: 'bottom'
            },
            calculable : true,
            xAxis : [
                {
                    type : 'category',
                    boundaryGap : false,
                    axisTick: {
                        show: false
                    },
                    data : ['1-2月','3-4月','5-6月','7-8月','9-10月','11-12月']
                }
            ],
            yAxis : [
                {
                    type : 'value',
                    axisTick: {
                        show: false
                    },
                    name: '交易条数（条）'
                }
            ],
            series: this.lineData.map(serie => ({
                name: serie.name,
                type: 'line', // 保证每个系列都是柱状图类型
                data: serie.counts,
                stack:  '总量'
            }))
        };
        // 使用刚指定的配置项和数据显示图表
        this.chartLine.setOption(option);
      },
        // 加载数据
        getGroup(){
          // 清除之前的图表
          if (this.chartLine) {
            this.chartLine.dispose();
            this.chartLine = null;
          }
          this.state.loading.spinning = true
          // 将响应式query返回起原始对象
          let p = toRaw(this.state.query)
          chartsGroup(p).then(res => {
              this.state.loading.spinning = false
              this.lineData = res.line
              console.log(res.line)
              this.drawLineChart(); // 在数据获取后调用绘图方法
          }).catch(err => {
              this.state.loading.spinning = false
              console.log(err)
          })
        },

        getPerson(searchValue){
          // 清除之前的图表
          if (this.chartLine) {
            this.chartLine.dispose();
            this.chartLine = null;
          }
          this.state.loading.spinning = true
          // 将响应式query返回起原始对象
          let p = { 'data': searchValue };
          chartsPerson(p).then(res => {
            this.state.loading.spinning = false
            this.lineData = res.line
            this.drawLineChart();
          }).catch(err => {
            this.state.loading.spinning = false
            console.log(err)
          })
        }
    }
  }
</script>

<style lang='less' scope>
    .line-wrap{
        width:100%;
        height:400px;
    }
</style>