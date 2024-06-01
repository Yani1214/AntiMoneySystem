<template>
  <div id="chartBar" class="bar-wrap"></div>
</template>

<script>
import * as echarts from 'echarts';
import 'echarts/theme/macarons'; // 引入主题
import {reactive, toRaw, markRaw,watch,defineProps} from 'vue';
import { chartsGroup,chartsPerson } from 'api/modules/api.charts';

export default {
  name: 'BarChart', // 修改为柱状图组件名称
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
      chartBar: null // 更正变量名
    }
  },
  mounted() {
    // 监听 searchValue 变化，触发 getPerson 事件
    this.$watch(() => this.$props.searchValue, (newValue) => {
      this.getPerson(newValue);
  });
    this.$watch(() => this.$props.update, (newValue, oldValue) => {
      if (newValue !== oldValue) {
        this.getGroup();
      }
    });

    this.$nextTick(() => {
      this.getGroup(); // 调用绘制柱状图的方法
    })
  },
  methods: {
    formatBarData(data) {
      return data.map(item => {
        return { value: item.count, name: item.name };
      });
    },
    drawBarChart() {
      let mytextStyle = {
        color: "#333",                          
        fontSize: 8,                            
      };
      let mylabel = {
        show: true,                 
        position: "top",          
        formatter: '{c}',      
        textStyle: mytextStyle
      };

      const formattedData = this.formatBarData(this.barData);
      this.chartBar = markRaw(echarts.init(document.getElementById('chartBar'), 'macarons'));
      this.chartBar.setOption({
        title: {
          text: '交易金额区间对应交易条数图', // 修改标题为柱状图
          subtext: '每人在各自交易区间内所占交易条数',
          x: 'center',
        },
        tooltip: {
          trigger: 'axis', // 修改触发方式为坐标轴触发
          formatter: "{a} <br/>{b} : {c}", // 修改提示框内容
        },
        legend: {
          data: formattedData.map(item => item.name), // 添加图例
          left: 'center',
          top: 'bottom'
        },
        xAxis: {
          type: 'category',
          data: ['<1k', '1k-5k', '5k-1w', '1w-5w', '5w-10w', '>10w']
        },
        yAxis: { 
          type: 'value',
          name: '交易条数', // 设置 y 轴名称
        },
        series: this.barData.map(serie => ({
          name: serie.name,
          type: 'bar', // 保证每个系列都是柱状图类型
          data: serie.counts,
          label: {
            show: true,
            position: 'top',
            formatter: '{c}', // 修改标签显示格式
            textStyle: mytextStyle
          }
        }))
      });
    },
    // 加载数据
    getGroup(){
      // 清除之前的图表
      if (this.chartBar) {
        this.chartBar.dispose();
        this.chartBar = null;
      }
      this.state.loading.spinning = true
      // 将响应式query返回起原始对象
      let p = toRaw(this.state.query)
      chartsGroup(p).then(res => {
        this.state.loading.spinning = false
        this.barData = res.bar
        this.drawBarChart(); // 在数据获取后调用绘图方法
      }).catch(err => {
        this.state.loading.spinning = false
        console.log(err)
      })
    },

    getPerson(searchValue){
      // 清除之前的图表
      if (this.chartBar) {
        this.chartBar.dispose();
        this.chartBar = null;
      }
      this.state.loading.spinning = true
      // 将响应式query返回起原始对象
      let p = { 'data': searchValue };
      chartsPerson(p).then(res => {
        this.state.loading.spinning = false
        this.barData = res.bar
        this.drawBarChart();
      }).catch(err => {
        this.state.loading.spinning = false
        console.log(err)
      })
    }

  }
}
</script>

<style lang='less' scoped>
.bar-wrap{
  width:100%;
  height:400px;
}
</style>
