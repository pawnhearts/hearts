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

      async function importKey(secret) {
        return await crypto.subtle.importKey(
          'raw',
          new TextEncoder().encode(secret),
          { name: 'HMAC', hash: 'SHA-256' },
          false,
          ['sign', 'verify'],
        )
      }const SECRET = 'SECRET'

      async function verifySignature(message, signature, secret) {
        const key = await importKey(secret)

        // Convert Base64 to Uint8Array
        const sigBuf = Uint8Array.from(atob(signature), c => c.charCodeAt(0))

        return await crypto.subtle.verify(
          'HMAC',
          key,
          sigBuf,
          new TextEncoder().encode(message),
        )
      }

      const urlParams = new URLSearchParams(window.location.search);
            const d = urlParams.get('telegram_id')
            const k = urlParams.get('key')
      if(!verifySignature(d, k, SECRET)) {
      alert('error')
      }
      this.telegram_id = d
      document.cookie = 'key='+k


      const sockets_bay_url = `wss://socketsbay.com/ws/${this.telegram_id}/`;
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
      const received = JSON.parse(evt.data);
      if(received['event'] === 'state'){
        this.game = received.data;
      }
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
