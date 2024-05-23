<template>
  <section>
    <a-button type="primary" size="small" @click="key_point">
      <template #icon></template>
      查看关键节点
    </a-button>

    <div style="width:100%;height:600px">
      <div ref="graph" style="width:100%;height:600px"></div>
    </div>
  </section>
</template>

<script>
import echarts from 'echarts';
import { reactive, ref, toRaw } from 'vue';
import { ZyNotification } from 'libs/util.toast';
import { analysisTrace } from 'api/modules/api.analysis';

function getColorByImportance(importance) {
  // 根据重要性计算颜色值
  if (importance <= 1.5) {
    // 绿色到黄色渐变
    const r = 0;
    const g = Math.floor(255 * importance * 4);
    const b = 0;
    return `rgb(${r},${g},${b})`;
  } else if (importance <= 3) {
    // 黄色到橙色渐变
    const r = Math.floor(255 * (importance - 0.25) * 4);
    const g = 255;
    const b = 0;
    return `rgb(${r},${g},${b})`;
  } else {
    // 橙色到红色渐变
    const r = 255;
    const g = Math.floor(255 * (1 - importance) * 2);
    const b = 0;
    return `rgb(${r},${g},${b})`;
  }
}

export default {
  setup() {
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
      echartsData: [],
      nodesRelation: [],
      echartsNode: [],
      myChart: '',
      options: {},
    };
  },

  mounted() {
    this.$echarts = echarts;
    this.searchGraph();
  },

  methods: {
    async searchGraph() {
      const neo4j = await import('neo4j-driver');
      const uri = 'bolt://localhost:7687/test';
      const user = 'neo4j';
      const password = 'XYZ67520x';
      const driver = neo4j.driver(uri, neo4j.auth.basic(user, password));
      const session = driver.session({ database: 'test' });

      try {
        const readQuery = `MATCH (n1)-[r:TRANSACTS_TO {label: 1}]->(n2) 
                            RETURN n1, r, n2`;

        const result = await session.run(readQuery, {});
        const records = result.records;

        records.forEach(record => {
          if (record._fields[0].properties.trans_name !== undefined) {
            this.echartsData.push({
              name: record._fields[0].identity.low.toString(),
              displayName: record._fields[0].properties.trans_name,
              category: 'FROM',
              symbolSize: 60 // 默认初始大小
            });
          }

          if (record._fields[2].properties.cp_name !== undefined) {
            this.echartsData.push({
              name: record._fields[2].identity.low.toString(),
              displayName: record._fields[2].properties.cp_name,
              category: 'TO',
              symbolSize: 60 // 默认初始大小
            });
          }

          this.nodesRelation.push({
            source: record._fields[1].start.low.toString(),
            target: record._fields[1].end.low.toString(),
            name: record._fields[1].type,
          });
        });

        // 去重
        const uniqueNodes = {};
        this.echartsData.forEach(node => {
          uniqueNodes[node.name] = node;
        });
        this.echartsNode = Object.values(uniqueNodes);

        const legend = [...new Set(this.echartsData.map(item => ({ name: item.category })))];
        this.category = legend;

        session.close();

        this.renderGraph();
      } catch (error) {
        console.error('Something went wrong: ', error);
      }
    },

    renderGraph() {
      const options = {
        tooltip: { show: false },
        legend: {
          type: 'scroll',
          orient: 'vertical',
          left: 10,
          top: 20,
          bottom: 20,
          data: this.category
        },
        series: [
          {
            categories: this.category,
            type: "graph",
            layout: "force",
            zoom: 0.6,
            draggable: true,
            roam: true,
            hoverAnimation: false,
            legendHoverLink: false,
            nodeScaleRatio: 0.6,
            focusNodeAdjacency: false,
            edgeSymbol: ["", "arrow"],
            edgeLabel: {
              normal: {
                show: false,
                textStyle: { fontSize: 12 },
                formatter(x) { return x.data.name; },
              },
            },
            label: {
              normal: {
                show: true,
                textStyle: { fontSize: 12 },
                color: "#f6f6f6",
                textBorderColor: '#000000',
                textBorderWidth: '1.3',
                formatter(params) { return params.data.displayName; },
              },
            },
            force: {
              repulsion: 200,
              gravity: 0.01,
              edgeLength: 400,
              layoutAnimation: true,
            },
            lineStyle: { normal: { curveness: 0.3 } },
            data: this.echartsNode,
            links: this.nodesRelation,
          }
        ]
      };

      this.myChart = this.$echarts.init(this.$refs.graph);
      this.myChart.setOption(options);

      this.myChart.on('mouseup', (params) => {
        const option = this.myChart.getOption();
        option.series[0].data[params.dataIndex].x = params.event.offsetX;
        option.series[0].data[params.dataIndex].y = params.event.offsetY;
        option.series[0].data[params.dataIndex].fixed = true;
        this.myChart.setOption(option);
      });
    },

    key_point() {
      this.state.loading.spinning = true;
      const query = toRaw(this.state.query);
      analysisTrace(query).then(res => {
        this.state.loading.spinning = false;
        if (res.result == 'ok') {
          ZyNotification.success(res.message || '分析完成');

          const traceData = res.data;
          const nodeData = this.echartsNode
          console.log(traceData)
          console.log(nodeData)

          nodeData.forEach(element => {
            const nodeIndex = element.name.toString()
            for (let i = 0; i < traceData.length; i++) {
              if (traceData[i][0].toString() === nodeIndex) {
                element.symbolSize = traceData[i][1]*15;
                // 更新节点颜色
                element.itemStyle = {
                  color: getColorByImportance(traceData[i][1])
                };
                break;
              }
            }
          });

          this.myChart.setOption({ 
            legend: { show: false },
            series: [{ data: this.echartsNode }] 
          });
          
        } else {
          ZyNotification.error(res.message || '分析失败');
        }
      }).catch(err => {
        this.state.loading.spinning = false;
        console.log(err);
      });
    }

  }
};
</script>

<style lang='less' scoped></style>
