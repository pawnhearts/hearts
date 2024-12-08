<template>
    <div>
<!--      <h4>Data passed</h4>-->
<!--      <h5>initData</h5>-->
<!--      <pre><code>{{ initData }}</code></pre>-->
<!--      <h5>initDataUnsafe</h5>-->
<!--      <pre><code>{{ initDataUnsafe }}</code></pre>-->
<!--              <button onclick="Telegram.WebApp.showAlert('Hello World!');">Launch Alert</button>-->
<!--        <button onclick="showPopup();">Launch Popup</button>-->

<!--        <h1>Links</h1>-->
<!--        <ul>-->
<!--            <li>-->
<!--                <a href="javascript:Telegram.WebApp.openTelegramLink('https://t.me/trendingapps');">Open link within Telegram</a>-->
<!--            </li>-->
<!--            <li>-->
<!--                <a href="javascript:Telegram.WebApp.openLink('https://ton.org/');">Open link in external browser</a>-->
<!--            </li>-->
<!--            <li>-->
<!--                <a href="javascript:Telegram.WebApp.openLink('https://telegra.ph/api',{try_instant_view:true});">Open link inside Telegram webview</a>-->
<!--            </li>-->
<!--        </ul>-->

      <Game  @move="move" @pass_cards="pass_cards" :telegram_id="telegram_id" :game="game" :hand="hand" :table="table" v-if="game.started_at !== null"></Game>
      <Lobby @vote_to_start="vote_to_start" :telegram_id="telegram_id" :game="game" v-if="game.started_at === null"></Lobby>
      <Chat @chat="send_chat" :telegram_id="telegram_id" :chat_messages="game.chat_messages"></Chat>
    </div>
</template>

<script>
import Lobby from './components/Lobby.vue'
import Game from './components/Game.vue'
import Chat from './components/Chat.vue'
import axios from 'axios'

const api = axios.create({
    baseURL: '/',
    headers: {
    }
});


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

      this.telegram_id = parseInt(Math.random()*33)

      const sockets_bay_url = `ws://127.0.0.1:8080/ws/${this.telegram_id}`;
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
      this.messages.push(received)
      if(received['event'] === 'state'){
        this.game = received.data;
      }
      if(received['event'] === 'hand'){
        this.hand = received.data.hand;
      }
      if(received['event'] === 'players'){
        this.game.players = received.data.players;
      }
      if(received['event'] === 'table'){
        this.table = received.data.table
        this.game.score_opened = received.data.score_opened
      }
      if(received['event'] === 'chat'){
        this.data.chat_messages.push(received.data)
      }
      if(received['event'] === 'waiting_pass'){
        this.game.waiting_for_pass = true
      }
      if(received['event'] === 'pass'){
        this.game.waiting_for_pass = false
      }
    },

    onSockerError(evt){
      this.connection_error = true;
    },
    send_chat(message) {
      // api.post('chat', {'message': message})
      this.websocket.send( JSON.stringify({event: 'message', 'message': message}) );
    },
    move(card) {
      // api.post('move', {'card': card})
      this.websocket.send( JSON.stringify({event: 'player_move', 'card': card}) );
    },
    pass_cards(cards) {
      if(this.game.waiting_for_pass) {
        // api.post('pass_cards', {'cards': cards})
        this.websocket.send(JSON.stringify({event: 'pass_cards', 'cards': cards}));
        this.game.waiting_for_pass = false
      }
    },
    vote_to_start() {
      // api.post('vote_to_start', {})
      this.websocket.send( JSON.stringify({event: 'vote_to_start'}) );
    },
  },
  mounted() {
    this.init_chat();
  },
  components: {Lobby, Game, Chat}
}

</script>

<style>
#app, body {
  width: 100%;
  height: 100%;
}
</style>
