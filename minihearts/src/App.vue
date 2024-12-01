<template>
    <div>
      <h4>Data passed</h4>
      <h5>initData</h5>
      <pre><code>{{ initData }}</code></pre>
      <h5>initDataUnsafe</h5>
      <pre><code>{{ initDataUnsafe }}</code></pre>
              <button onclick="Telegram.WebApp.showAlert('Hello World!');">Launch Alert</button>
        <button onclick="showPopup();">Launch Popup</button>

        <h1>Links</h1>
        <ul>
            <li>
                <a href="javascript:Telegram.WebApp.openTelegramLink('https://t.me/trendingapps');">Open link within Telegram</a>
            </li>
            <li>
                <a href="javascript:Telegram.WebApp.openLink('https://ton.org/');">Open link in external browser</a>
            </li>
            <li>
                <a href="javascript:Telegram.WebApp.openLink('https://telegra.ph/api',{try_instant_view:true});">Open link inside Telegram webview</a>
            </li>
        </ul>
    </div>
</template>

<script>
// import HelloWorld from './components/HelloWorld.vue'



export default {
  name: 'App',
  computed: {
    initData:  () => { return window.Telegram.WebApp.initData; }
  },
  components: {
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
