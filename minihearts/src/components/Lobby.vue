<script setup>
export default {
  name: 'Lobby',
  data(){
    return {
      telegram_id: 0,
      game: {},
      connection_ready: false,
      connection_error: false,
      websocket: null,
      new_message: "",
      messages: []
    }
  },
  methods:{
    init_chat() {
      //ask for a nickname

      //connect to Sockets Bay
      var sockets_bay_url = `wss://socketsbay.com/wss/v2/100/${this.sockets_bay_api_key}/`;
      this.websocket      = new WebSocket(sockets_bay_url);
      //
      this.websocket.onopen    = this.onSocketOpen;
      this.websocket.onmessage = this.onSocketMessage;
      this.websocket.onerror   = this.onSockerError;
    },
    onSocketOpen(evt){
      this.connection_ready = true;
    },
    onSocketMessage(evt){
      //we parse the json that we receive
      var received = JSON.parse(evt.data);
      //check if it's our message or from a friend
      this.messages.push( { from: "other", message: received.message } );
      //scroll to the bottom of the messages div
      const messages_div = document.getElementById('messages');
      messages_div.scrollTo({top: messages_div.scrollHeight, behavior: 'smooth'});
    },

    onSockerError(evt){
      this.connection_error = true;
    },

    send_message() {
      var to_send = { from: this.nickname, message: this.new_message };
      this.websocket.send( JSON.stringify(to_send) );
      this.messages.push( { from: "me"   , message: this.new_message } );
      this.new_message = "";
    }
  },
  mounted() {
    this.init_chat();
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
</template>

<style scoped>

</style>
