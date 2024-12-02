<script>
export default {
  name: 'Lobby',
  props: ['telegram_id', 'game'],
  emits: ['chat', 'vote_to_start'],
  data(){
    return {
    }
  },
  methods: {},
  mounted() {

  }
}
</script>

<template>
  <div>
    <h1>Lobby</h1>
    Players:
    <p v-for="player in game.players" :key="player.telegram_id">
      {{player.telegram_id}}
    </p>
    <button @click="$emit('vote_to_start')">start with bots</button>
  </div>
</template>

<style scoped>

</style>
