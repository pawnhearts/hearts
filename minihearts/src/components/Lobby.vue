<script setup>
export default {
  name: 'Lobby',
  props: ['telegram_id', 'game'],
  emits: ['chat', 'start'],
  data(){
    return {
      message:''
    }
  },
  methods: {},
  mounted() {

  }
}
</script>

<template>
  <div>
    Players:
    <span v-for="player in game.players" :key="player.id">
      {{player.id}}
    </span>
  </div>
</template>

<style scoped>

</style>
