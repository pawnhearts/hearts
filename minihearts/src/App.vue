<template>
    <div>
      <h4>Data passed</h4>
      <h5>initData</h5>
      <pre><code>{{ initData }}</code></pre>
      <h5>initDataUnsafe</h5>
      <pre><code>{{ initDataUnsafe }}</code></pre>
    </div>
  <LoginWidget
    bot-username="samplebot"
    @auth="handleUserAuth"
  />
</template>

<script>
// import HelloWorld from './components/HelloWorld.vue'


// import { LoginWidget } from 'vue-tg'
// import { LoginWidgetUser } from 'vue-tg'
import {
  useWebApp,
  useWebAppHapticFeedback,
  useWebAppMainButton,
  useWebAppNavigation,
  useWebAppPopup,
  useWebAppQrScanner,
  useWebAppTheme,
  useWebAppViewport,
  useWebAppBiometricManager,
} from 'vue-tg'
const {platform, initData, initDataUnsafe, sendData } = useWebApp()


export default {
  name: 'App',
  components: {
    HelloWorld
  }
}

</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
