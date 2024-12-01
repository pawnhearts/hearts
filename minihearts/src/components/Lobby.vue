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
  <div>
    Chat:
    <p v-for="chat in game.chat_messages" :key="chat.created_at">
      {{chat.player.id}} {{chat.private_to}} {{chat.message}} {{chat.creat}}
    </p>
  </div>
  <input type="text" v-model="message"><button @click="$emit('chat', this.message)">send</button>
</template>

<style scoped>

</style>
