<template>
  <div class="info-list">
    <div v-for="(item, index) in infoItems" :key="item.person_number" class="user-info">
      <h3 @click="toggleDetails(item.person_number)">
        {{ item.person_name }}
        <a-icon :type="item.expanded ? 'up' : 'down'" />
      </h3>
      <div v-if="item.expanded">
        <p><strong>ID:</strong> {{ item.person_number }}</p>
        <p><strong>身份证号:</strong> {{ item.person_id }}</p>
        <p><strong>卡号:</strong>
        <ul>
          <li v-for="card in item.person_card" :key="card">{{ card }}</li>
        </ul>
        </p>
        <p><strong>账号:</strong>
        <ul>
          <li v-for="account in item.person_account" :key="account">{{ account }}</li>
        </ul>
        </p>
        <div>
          <strong>模型检测结果:</strong>
          <p>{{ item.model_result }}</p>
        </div>
        <div>
          <strong>人工审核信息:</strong>
          <a-textarea v-model:value="item.manual_review" placeholder="请输入人工审核信息"></a-textarea>
          <!-- <input v-model="item.manual_review" placeholder="请输入人工审核信息" /> -->
          <a-button type="primary" @click="saveReview(item, index)">{{ item.isSaved ? '修改' : '保存' }}</a-button>
        </div>
      </div>
    </div>
    <!-- 分页控件 -->
    <div class="pagination-wrapper">
      <a-pagination :current="currentPage" :total="totalItems" :pageSize="pageSize" :pageSizeOptions="[]"
        @change="handlePageChange" show-total show-quick-jumper hideOnSinglePage />
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  props: {
    searchQuery: {
      type: String,
      required: true,
    },
    currentPage: {
      type: Number,
      required: true,
    },
    pageSize: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      infoItems: [],
      totalItems: 0,
    };
  },
  watch: {
    searchQuery(newQuery) {
      console.log("searchQuery changed:", newQuery); // 调试信息
      this.fetchUserData(newQuery, this.currentPage, this.pageSize);
    },
    currentPage(newPage) {
      this.fetchUserData(this.searchQuery, newPage, this.pageSize);
    },
  },
  methods: {
    toggleDetails(person_number) {
      const user = this.infoItems.find(item => item.person_number === person_number);
      user.expanded = !user.expanded;
    },
    async fetchUserData(query, page, pageSize) {
      try {
        console.log(`Fetching data with query: ${query}, page: ${page}, pageSize: ${pageSize}`);
        const response = await axios.get('http://127.0.0.1:3091/getUserInfo', {
          params: { query, page, pageSize }
        });
        console.log("Response data:", response.data);
        this.infoItems = response.data.items.map(user => ({
          ...user,
          expanded: false,
        }));
        console.log("Info items:", this.infoItems);
        this.totalItems = response.data.total;
      } catch (error) {
        console.error('Error fetching user data:', error);
      }
    },
    async saveReview(item, index) {
      try {
        const data = {
          person_number: item.person_number,
          manual_review: item.manual_review
        };
        console.log("Sending data:", data);  // 打印发送的数据以便调试
        const response = await axios.post('http://127.0.0.1:3091/saveManualReview', data, {
          headers: {
            'Content-Type': 'application/json'
          }
        });
        if (response.data.message) {
          this.infoItems[index]["isSaved"] = true
          this.$message.success('人工审核信息保存成功');
        }
      } catch (error) {
        console.error('Error saving review:', error);
        this.$message.error('保存失败，请稍后再试');
      }
    },
    handlePageChange(page) {
      this.$emit('updatePage', page);
      this.fetchUserData(this.searchQuery, page, this.pageSize);
    },
  },

  mounted() {
    // 初次加载第一页数据
    // this.fetchUserData(this.searchQuery, this.currentPage, this.pageSize);
  },
};
</script>

<style scoped>
.info-list {
  width: 100%;
  padding: 10px;
  background-color: #f5f5f5;
  overflow-y: auto;
}

.user-info {
  margin-bottom: 10px;
  /* 减少外部空白 */
  padding: 5px;
  /* 减少内部空白 */
  border: 1px solid #d9d9d9;
  border-radius: 2px;
  /* 减少边框圆角 */
  cursor: pointer;
  font-size: 14px;
  /* 调整字体大小 */
}

.user-info h3 {
  font-size: 16px;
  /* 调整标题字体大小 */
}

.user-info p {
  font-size: 14px;
  /* 调整段落字体大小 */
}

.user-info ul {
  font-size: 14px;
  /* 调整列表字体大小 */
}

.user-info a-textarea {
  font-size: 14px;
  /* 调整文本框字体大小 */
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.ant-pagination-options {
  display: none !important;
  /* 强制隐藏几条一页的选项 */
}

.ant-pagination-item-active {
  border-color: #1890ff;
}

.ant-pagination-item-active a {
  color: #1890ff;
}

.ant-pagination-item {
  min-width: 32px;
  height: 32px;
  line-height: 30px;
  margin: 0 4px;
  border-radius: 4px;
}

.ant-pagination-item a {
  display: block;
  width: 100%;
  height: 100%;
  text-align: center;
}

.ant-pagination-item:hover a {
  color: #1890ff;
}

.ant-pagination-item:hover {
  border-color: #1890ff;
}
</style>
