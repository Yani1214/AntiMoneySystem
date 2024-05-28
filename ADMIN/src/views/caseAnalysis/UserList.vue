<template>
  <div class="info-list">
    <div v-for="(item, index) in infoItems" :key="item.person_number" class="user-info">
      <h3 @click="toggleDetails(item.person_number)">
        {{ item.person_name }}
        <a-icon :type="item.expanded ? 'up' : 'down'" />
      </h3>
      <div v-if="item.expanded">
        <p><span class="info-title">ID:</span> <span class="info-detail">{{ item.person_number }}</span></p>
        <p><span class="info-title">身份证号:</span> <span class="info-detail">{{ item.person_id }}</span></p>
        <p><span class="info-title">卡号:</span>
          <a @click="toggleShowCards(item)">显示卡号 ({{ item.person_card.length }})</a>
          <ul v-if="item.showCards">
            <li v-for="cardInfo in item.cardLabels" :key="cardInfo.card" class="card-info">
              <span class="card-number">{{ cardInfo.card }}</span>
              <span class="suspicion-result">({{ getSuspicionForCard(cardInfo.card) }})</span>
              <a-select v-model:value="cardInfo.label" size="small" class="label-select" @change="value => updateLabel(item, cardInfo.card, value)">
                <a-select-option value="0">0</a-select-option>
                <a-select-option value="1">1</a-select-option>
              </a-select>
            </li>
          </ul>
        </p>
        <p><span class="info-title">账号:</span>
          <a @click="toggleShowAccounts(item)">显示账号 ({{ item.person_account.length }})</a>
          <ul v-if="item.showAccounts">
            <li v-for="account in item.person_account" :key="account">{{ account }}</li>
          </ul>
        </p>
        <div class="review-section">
          <strong>审核结果:</strong>
          <a-textarea v-model:value="item.manual_review" placeholder="请输入人工审核信息"></a-textarea>
          <a-button type="primary" size="small" @click="saveReview(item, index)" class="save-button">{{ item.isSaved ? '修改' : '保存' }}</a-button>
        </div>
      </div>
    </div>
    <div class="pagination-wrapper">
      <a-pagination :current="currentPage" :total="totalItems" :pageSize="pageSize" :pageSizeOptions="[]" @change="handlePageChange" show-total show-quick-jumper hideOnSinglePage />
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
      suspicionData: [], // 用于存储模型检测结果
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
    toggleShowCards(item) {
      item.showCards = !item.showCards;
    },
    toggleShowAccounts(item) {
      item.showAccounts = !item.showAccounts;
    },
    async fetchSuspicionData() {
      try {
        const response = await axios.get('http://127.0.0.1:3091/getSuspicionData');
        this.suspicionData = response.data;
      } catch (error) {
        console.error('Error fetching suspicion data:', error);
      }
    },
    getSuspicionForCard(card) {
      const suspicionInfo = this.suspicionData.find(item => item.card === card);
      return suspicionInfo ? suspicionInfo.suspicion.toFixed(2) : '空';
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
          isSaved: !!user.manual_review, // 如果有人工审核信息，则设置 isSaved 为 true
          showCards: false, // 初始化 showCards
          showAccounts: false, // 初始化 showAccounts
          // 初始化 cardLabels 时绑定每个卡号对应的标签
          cardLabels: user.person_card.map((card, index) => ({
            card,
            label: user.labels[index] // 绑定每个卡号的标签
          }))
        }));
        console.log("Info items:", this.infoItems);
        this.totalItems = response.data.total;
      } catch (error) {
        console.error('Error fetching user data:', error);
      }
    },
    async updateLabel(item, card, value) {
      try {
        const response = await axios.post('http://127.0.0.1:3091/updateLabel', {
          person_number: item.person_number,
          card: card,
          label: value
        });
        if (response.data.success) {
          this.$message.success('标签更新成功');
          // 确保本地数据也更新
        } else {
          this.$message.error('标签更新失败');
        }
      } catch (error) {
        console.error('Error updating label:', error);
        this.$message.error('标签更新失败，请稍后再试');
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
    async mounted() {
        await this.fetchSuspicionData(); // 获取模型检测结果数据
        this.fetchUserData(this.searchQuery, this.currentPage, this.pageSize); // 初次加载第一页数据
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
  padding: 5px;
  border: 1px solid #d9d9d9;
  border-radius: 2px;
  cursor: pointer;
  font-size: 14px;
}

.user-info h3 {
  font-size: 16px;
}

.user-info p {
  font-size: 14px;
}

.user-info .info-title {
  font-weight: bold;
  color: #333;
}

.user-info .info-detail {
  color: #555;
}

.user-info ul {
  font-size: 14px;
}

.card-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-number {
  flex: 2;
  width: 40%;
  text-align: left;
}

.suspicion-result {
  flex: 1;
  width: 30%;
  text-align: center;
}

.label-select {
  flex: 1;
  width: 30%;
  font-size: 12px;
  height: 24px;
  text-align: right;
}

.review-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.review-section a-textarea {
  flex: 1;
  font-size: 14px;
}

.save-button {
  font-size: 12px;
  height: 30px;
  line-height: 1.5;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.ant-pagination-options {
  display: none !important;
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

.suspicion-result {
  font-weight: bold;
  color: #f56c6c; /* 可以根据需求修改颜色 */
}
</style>