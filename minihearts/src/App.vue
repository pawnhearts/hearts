<template>
    <div>
      <h4>Data passed</h4>
      <h5>initData</h5>
      <pre><code>{{ initData }}</code></pre>
      <h5>initDataUnsafe</h5>
      <pre><code>{{ initDataUnsafe }}</code></pre>
              <button onclick="Telegram.WebApp.showAlert('Hello World!');">Launch Alert</button>
        <button onclick="showPopup();">Launch Popup</button>

        <h1>Links</h1>
        <ul>
            <li>
                <a href="javascript:Telegram.WebApp.openTelegramLink('https://t.me/trendingapps');">Open link within Telegram</a>
            </li>
            <li>
                <a href="javascript:Telegram.WebApp.openLink('https://ton.org/');">Open link in external browser</a>
            </li>
            <li>
                <a href="javascript:Telegram.WebApp.openLink('https://telegra.ph/api',{try_instant_view:true});">Open link inside Telegram webview</a>
            </li>
        </ul>

      <Game @chat="send_chat" @move="move" @pass_cards="pass_cards" :telegram_id="telegram_id" :game="game" v-if="game.started_at"></Game>
      <Lobby @chat="send_chat" :telegram_id="telegram_id" :game="game" v-if="!game.started_at"></Lobby>
    </div>
</template>

<script>
import Lobby from './components/Lobby.vue'
import Game from './components/Game.vue'



export default {
  name: 'App',
  data(){
    return {
      telegram_id: 0,
      game: {},
      hand: [],
      table: [],
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
      if(received['event'] === 'hand'){
        this.hand = received.data;
      }
      if(received['event'] === 'players'){
        this.players = received.data.players;
      }
      if(received['event'] === 'table'){
        this.table = received.data.table
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
    },
    send_chat(message) {
      this.websocket.send( JSON.stringify({event: 'chat', data: {'message': message}}) );
    },
    move(card) {
      this.websocket.send( JSON.stringify({event: 'player_move', data: {'card': card}}) );
    },
    pass_cards(cards) {
      if(this.game.waiting_for_pass) {
        this.websocket.send(JSON.stringify({event: 'pass_cards', data: {'cards': cards}}));
      }
    },
  },
  mounted() {
    this.init_chat();
  },
  components: {Lobby, Game}
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
