<template>
  <div v-for="player in game.players">
    {{player.telegram_id}}
    <div v-if="player.telegram_id === telegram_id">
      <button v-for="c in hand" @click="$emit('move', c)">{{c}}</button>
    </div>
  </div>
  <p v-for="c in table">{c}</p>
</template>

<script setup>
export default {
  name: 'Game',
  props: ['telegram_id', 'game', 'hand'],
  emits: ['chat', 'move', 'pass_cards'],
  data(){
    return {
    }
  },
  methods: {
  },
  mounted() {

  }
}

</script>
