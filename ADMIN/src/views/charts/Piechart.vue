<template>
    <div id="chartPie" class="pie-wrap"></div>
</template>

<script>
import * as echarts from 'echarts';
import {reactive, toRaw} from 'vue';
import 'echarts/theme/shine'; //引入主题
import { chartsGroup,chartsPerson } from 'api/modules/api.charts';
import { int } from 'neo4j-driver';

export default {
  name: 'Pinechart', 
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
          chartPie: null
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
    formatPieData(data) {
      return data.map(item => {
        return { value: item.count, name: item.name };
      });
    },
    drawPieChart() {
      let mytextStyle = {
        color: "#333",                          
        fontSize: 18,                            
      };
      let mylabel = {
        show: true,                 
        position: "right",          
        offset: [30, 40],             
        formatter: '{b} : {c} ({d}%)',      
        textStyle: mytextStyle
      };

      const formattedData = this.formatPieData(this.pieData);
      this.chartPie = echarts.init(document.getElementById('chartPie'),'shine');
      this.chartPie.setOption({
        title: {
          text: this.pieText.main,
          subtext: this.pieText.sub, // 这里分为洗钱团伙和个人
          x: 'center'
        },
        tooltip: {
          trigger: 'item',
          formatter: "{a} <br/>{b} : {c} ({d}%)",
        },
        legend: {
          data: formattedData.map(item => item.name),
          left:"center",                              
          top:"bottom",                              
          orient:"horizontal",                        
        },
        series: [
          {
            name: '交易人员',
            type: 'pie',
            radius: ['50%', '70%'],
            center: ['50%', '50%'],
            data: formattedData,
            animationEasing: 'cubicInOut',
            animationDuration: 2600,
            label: {           
              emphasis: mylabel
            }
          }
        ]
      });
    },
    // 加载数据
    getGroup(){
      // 清除之前的图表
      if (this.chartPie) {
        this.chartPie.dispose();
        this.chartPie = null;
      }
      this.state.loading.spinning = true
      // 将响应式query返回起原始对象
      let p = toRaw(this.state.query)
      chartsGroup(p).then(res => {
        this.state.loading.spinning = false
        this.pieData = res.pie
        this.pieText = res.text
        console.log(res.pie)
        console.log(res.text)
        this.drawPieChart(); // 在数据获取后调用绘图方法
        this.$emit('updateResult',this.update);
      }).catch(err => {
        this.state.loading.spinning = false
        console.log(err)
      })
    },

    getPerson(searchValue){
      // 清除之前的图表
      if (this.chartPie) {
        this.chartPie.dispose();
        this.chartPie = null;
      }
      this.state.loading.spinning = true
      // 将响应式query返回起原始对象
      let p = { 'data': searchValue };
      chartsPerson(p).then(res => {
        this.state.loading.spinning = false
        this.pieData = res.pie
        this.pieText = res.text
        console.log(res.text)
        this.drawPieChart();
        this.$emit('searchResult', searchValue);
      }).catch(err => {
        this.state.loading.spinning = false
        console.log(err)
      })
    }

  }
}
</script>

<style lang='less' scope>
    .pie-wrap{
        width:100%;
        height:400px;
    }
</style>