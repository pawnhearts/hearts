<script setup>
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
    Players:
    <span v-for="player in game.players" :key="player.telegram_id">
      {{player.telegram_id}}
    </span>
  </div>
</template>

<style scoped>

</style>
