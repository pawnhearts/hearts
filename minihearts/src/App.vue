<template>
    <div>
      <h4>Data passed</h4>
      <h5>initData</h5>
      <pre><code>{{ initData }}</code></pre>
      <h5>initDataUnsafe</h5>
      <pre><code>{{ initDataUnsafe }}</code></pre>
      {{window.Telegram.WebApp.initData}}
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
