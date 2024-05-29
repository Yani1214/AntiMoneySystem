<template>
  <div v-show="getShow">
    <h2 class="login-title">登录</h2>
    <a-form :model="state.formState" name="normal_login" class="login-form" @finish="onFinish" @finishFailed="onFinishFailed">
      <a-form-item name="username" :rules="[{ required: true, message: '请输入用户名!' }]">
        <a-input v-model:value="state.formState.username" allowClear autocomplete="off" size="large" placeholder="用户名">
          <template #prefix>
            <IconFont type="icon-yonghuming" style="font-size: 18px" />
          </template>
        </a-input>
      </a-form-item>
      <a-form-item name="password" :rules="[{ required: true, message: '请输入密码!' }]">
        <a-input-password v-model:value="state.formState.password" allowClear autocomplete="off" placeholder="密码" size="large">
          <template #prefix>
            <IconFont type="icon-mima" style="font-size: 18px" />
          </template>
        </a-input-password>
      </a-form-item>
      <a-form-item>
        <a-form-item name="remember" no-style>
          <a-checkbox v-model:checked="state.formState.remember">记住密码</a-checkbox>
        </a-form-item>
      </a-form-item>
      <a-form-item>
        <a-button type="primary" class="form-button" :disabled="disabled" html-type="submit" size="large"> 登录 </a-button>
      </a-form-item>
    </a-form>
    <div class="login-btn-container">
      <a-space class="login-btn-list">
        <a-button @click="setLoginState('register')" type="primary" class="form-button" size="large"> 注册 </a-button>
      </a-space>
    </div>
  </div>
</template>

<script setup>
  import { reactive, ref, computed } from "vue";
  import { useAuthStore } from "../../../../stores/auth.js";
  import { useLoginState } from "@/hooks/sys/useLogin.js";

  const authStore = useAuthStore();
  const { setLoginState, getLoginState } = useLoginState();
  const getShow = computed(() => {
    return getLoginState.value === "login";
  });

  const state = reactive({
    formState: {
      username: "admin",
      password: "123456",
      remember: false
    },
    captchaSvg: ""
  });

  const onFinish = (values) => {
    authStore
      .login(values)
      .then((res) => {})
      .catch((err) => {});
  };
  const onFinishFailed = (errorInfo) => {
    console.log("Failed:", errorInfo);
  };
  const disabled = computed(() => {
    return !(state.formState.username && state.formState.password);
  });
</script>

<style lang="scss" scoped>
  .login-title {
    margin-bottom: 30px;
    text-align: center;
  }

  .login-form {
    max-width: 400px;
    margin: 0 auto;
    background-color: #fff;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .form-button {
    width: 100%;
    margin-top: 10px;
  }

  .login-btn-container {
    width: 100%;
    max-width: 400px;
    margin: 0 auto;
    padding: 20px 0;
  }

  .login-btn-list {
    display: flex;
    justify-content: center;
  }
</style>
