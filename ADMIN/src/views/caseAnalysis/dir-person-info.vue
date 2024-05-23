<template>
  <section style="display: flex; flex-direction: column; height: 100%">
    <!-- 搜索框 -->
    <div class="search-bar">
      <a-row type="flex" justify="start" align="middle" :gutter="10">
        <a-col :span="18">
          <a-input v-model="searchValue" placeholder="请输入需要查询的用户名称" @pressEnter="search"></a-input>
        </a-col>
        <a-col :span="6">
          <a-button type="primary" size="middle" @click="search">查询</a-button>
        </a-col>
      </a-row>
    </div>

    <div style="display: flex; flex: 1">
      <!-- 左侧用户列表 -->
      <div class="left-panel">
        <UserList ref="userList" :searchQuery="searchValue" :currentPage="currentPage" :pageSize="pageSize" @updatePage="handlePageChange" />
      </div>

      <!-- 右侧图表 -->
      <div class="right-panel">
        <div style="width: 100%; height: 100%">
          <div ref="graph" style="width: 100%; height: 100%"></div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
  import echarts from "echarts";
  import UserList from "./UserList.vue";

export default {
  data () {
    components: {
      UserList
    },
    return {
      // 绘制知识图谱的节点数据
      echartsData: [],
      nodesRelation: [],
      echartsNode: [],
      // 防止出现多个echarts初始化的情况
      myChart: '',
      options: {},
      searchValue: '杨小琴', // 输入框的值
      currentPage: 1, // 当前页码
      totalItems: 0, // 总记录数
      pageSize: 10 // 每页记录数
    }
  },
  mounted () {
    this.$echarts = echarts;
    // this.search(); // 在组件挂载时加载默认数据
    // 初次加载第一页数据，不传递查询参数
    this.currentPage = this.currentPage || 1; // 确保在初始加载时 `currentPage` 有默认值
    if (this.$refs.userList) {
      this.$refs.userList.fetchUserData("", this.currentPage, this.pageSize);
    }
    this.searchGraph()
  },
  methods: {
    search() {
      // 点击查询按钮时触发的方法
      if (this.$refs.userList) {
        this.$refs.userList.fetchUserData(this.searchValue, this.currentPage, this.pageSize);
      }
      console.log("searchValue:", this.searchValue);
      this.resetState();
      this.searchGraph();
    },
    handlePageChange(page) {
      this.currentPage = page;
      this.search();
    },
    updateTotalItems(total) {
      this.totalItems = total;
    },
    async searchGraph () {
      // 在Vue组件中
      const neo4j = await import('neo4j-driver');
      const uri = 'bolt://localhost:7687/test'; //ip地址
      const user = 'neo4j'; //账号
      const password = 'XYZ67520x';//密码
      const driver = neo4j.driver(uri, neo4j.auth.basic(user, password))
      const session = driver.session({ database: 'test' })
      
      try {
        // const readQuery1 = `MATCH (n:Person)  RETURN n.name AS name `
        // const readQuery2 = `MATCH p=()-->() RETURN p LIMIT 20`
        // const readQuery2 = 'MATCH p=()-[r:TRANSACTS_TO]->() RETURN p LIMIT 30'
        const readQuery2 = `MATCH (n1:Node1)-[r:TRANSACTS_TO]->(n2:Node2) 
                            WHERE n1.trans_name = $searchValue OR n2.cp_name = $searchValue 
                            RETURN n1, r, n2
                            LIMIT 20`;
          // const readQuery2 = `MATCH (p:Node1)
          //               WHERE p.trans_name = "杨小琴"
          //               RETURN p.trans_name AS trans_name LIMIT 20`

          var me = { records: [] };
          // const result = await session.run(readQuery2, {})
          const result = await session.run(readQuery2, { searchValue: this.searchValue });
          console.log(this.searchValue);

          // console.log(result)
          me.records = result.records;
          // console.log(me.records)
          // console.log(me.records[0]._fields[0].properties.trans_name)

          for (let i = 0; i < me.records.length; i++) {
            // this.echartsData.push({
            //   name: me.records[i]._fields[0].segments[0].start.properties.trans_name,
            //   // category: me.records[i]._fields[0].segments[0].start.labels[0]
            //   category: 'Node1'
            // });
            if (me.records[i]._fields[0].properties.trans_name !== undefined) {
              this.echartsData.push({
                name: me.records[i]._fields[0].properties.trans_name,
                category: "FROM"
              });
            }
            // this.echartsData.push({
            //   name: me.records[i]._fields[0].segments[0].end.properties.cp_name,
            //   // category: me.records[i]._fields[0].segments[0].end.labels[0]
            //   category: 'Node2'
            // });

            if (me.records[i]._fields[2].properties.cp_name !== undefined) {
              this.echartsData.push({
                name: me.records[i]._fields[2].properties.cp_name,
                category: "TO"
              });
            }

            // this.nodesRelation.push({
            //   source: me.records[i]._fields[0].segments[0].start.properties.trans_name,
            //   target: me.records[i]._fields[0].segments[0].end.properties.cp_name,
            //   name: me.records[i]._fields[0].segments[0].relationship.type,
            // });

            if (me.records[i]._fields[0].properties.trans_name !== undefined && me.records[i]._fields[2].properties.cp_name !== undefined) {
              this.nodesRelation.push({
                source: me.records[i]._fields[0].properties.trans_name,
                target: me.records[i]._fields[2].properties.cp_name,
                name: me.records[i]._fields[1].type
              });
            }
          }
          // console.log(this.echartsData)
          // console.log(this.nodesRelation)

          //删除arr中的重复对象
          var arrId = [];
          var legend = [];
          for (var item of this.echartsData) {
            legend.push({ name: item.category });
            if (arrId.indexOf(item.name) == -1) {
              arrId.push(item.name);
              this.echartsNode.push(item);
            }
          }

          // console.log(this.echartsNode)
          this.category = Array.from(new Set(legend));
          session.close();
          // me.closeLoading(false);

          var options = {};
          options = {
            // title: {
            //   text: "生物语义网络图谱",  // 标题
            // },
            tooltip: {
              //弹窗
              show: false
              // enterable: true,//鼠标是否可进入提示框浮层中
              // formatter: formatterHover,//修改鼠标悬停显示的内容
            },

            legend: {
              type: "scroll",
              orient: "vertical",
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
                symbolSize: 60,
                // 节点是否可以拖动
                draggable: true,
                roam: true,
                hoverAnimation: false,
                legendHoverLink: false,
                nodeScaleRatio: 0.6, //鼠标漫游缩放时节点的相应缩放比例，当设为0时节点不随着鼠标的缩放而缩放
                focusNodeAdjacency: false, //是否在鼠标移到节点上的时候突出显示节点以及节点的边和邻接节点。
                // categories: categories,

              // itemStyle: {
              //   color: "#67A3FF",
              // },
              
              edgeSymbol: ["", "arrow"],
              // edgeSymbolSize: [80, 10],
              edgeLabel: {
                normal: {
                  show: false,
                  textStyle: {
                    fontSize: 12,
                  },

                    formatter(x) {
                      return x.data.name;
                    }
                  }
                },

                label: {
                  normal: {
                    show: true,
                    textStyle: {
                      fontSize: 12
                    },
                    color: "#f6f6f6",
                    textBorderColor: "#000000",
                    textBorderWidth: "1.3",
                    // 多字换行
                    formatter: function (params) {
                      // console.log(params);
                      var newParamsName = "";
                      var paramsNameNumber = params.name.length;
                      var provideNumber = 7; //一行显示几个字
                      var rowNumber = Math.ceil(paramsNameNumber / provideNumber);

                      if (paramsNameNumber > provideNumber) {
                        for (var p = 0; p < rowNumber; p++) {
                          var tempStr = "";

                          var start = p * provideNumber;

                          var end = start + provideNumber;

                          if (p == rowNumber - 1) {
                            tempStr = params.name.substring(start, paramsNameNumber);
                          } else {
                            tempStr = params.name.substring(start, end) + "\n\n";
                          }

                          newParamsName += tempStr;
                        }
                      } else {
                        newParamsName = params.name;
                      }

                      return newParamsName;
                    }
                  }
                },

                force: {
                  repulsion: 200, // 节点之间的斥力因子。支持数组表达斥力范围，值越大斥力越大。

                  gravity: 0.01, // 节点受到的向中心的引力因子。该值越大节点越往中心点靠拢。

                  edgeLength: 400, // 边的两个节点之间的距离，这个距离也会受 repulsion影响 。值越大则长度越长

                  layoutAnimation: true // 因为力引导布局会在多次迭代后才会稳定，这个参数决定是否显示布局的迭代动画

                  // 在浏览器端节点数据较多（>100）的时候不建议关闭，布局过程会造成浏览器假死。
                },

                data: this.echartsNode,

                links: this.nodesRelation

                // categories: this.categories
              }
            ]
          };
          console.log(this.echartsData);
          console.log(this.echartsNode);
          console.log(this.nodesRelation);
          console.log(this.category);
          // console.log(options.series)
          console.log(this, 66633);

          //节点自定义拖拽不回弹

          this.myChart = this.$echarts.init(this.$refs.graph);

          // console.log(this.$refs.graph);

          const chart = this.myChart;

          this.myChart.setOption(options);

          chart.on("mouseup", function (params) {
            var option = chart.getOption();

            option.series[0].data[params.dataIndex].x = params.event.offsetX;

            option.series[0].data[params.dataIndex].y = params.event.offsetY;

            option.series[0].data[params.dataIndex].fixed = true;

            chart.setOption(option);
          });
        } catch (error) {
          console.error("Something went wrong: ", error);
        } finally {
          // await session.close()
        }
      },

      resetState() {
        // 将数据属性重置为其初始值
        // Object.assign(this.$data, this.$options.data.call(this));
        // 获取初始数据对象
        const initialData = this.$options.data.call(this);
        // 排除 searchValue 属性
        const { searchValue, ...restData } = initialData;
        // 仅复制除了 searchValue 之外的属性到 $data 中
        Object.assign(this.$data, restData);
      }
    }
  };
</script>

<style lang="less" scoped>
  .left-panel {
    flex: 1 1 33%; /* 左侧面板占三分之一 */
    max-width: 33%;
    box-sizing: border-box;
    padding-right: 10px;
  }

  .right-panel {
    flex: 1 1 67%; /* 右侧面板占三分之二 */
    max-width: 67%;
    box-sizing: border-box;
    padding-left: 10px;
  }
</style>
