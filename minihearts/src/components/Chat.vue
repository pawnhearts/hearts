<script setup>

export default {
  name: 'Chat',
  props: ['telegram_id', 'chat_messages'],
  emits: ['chat'],
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
    Chat:
    <p v-for="chat in chat_messages" :key="chat.created_at">
      {{chat.player.telegram_id}} {{chat.private_to}} {{chat.message}} {{chat.creat}}
    </p>
  </div>
  <input type="text" v-model="message"><button @click="$emit('chat', this.message)">send</button>
</template>

<style scoped>

</style>
