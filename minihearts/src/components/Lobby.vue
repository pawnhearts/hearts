<script setup>

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
</template>

<style scoped>

</style>
