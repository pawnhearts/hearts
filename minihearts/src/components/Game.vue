<template>
  <div class="playingCards fourColours rotateHand">
  <h1>game</h1>
  <div v-for="player in game.players">
    {{player.telegram_id}}
    <div v-if="player.telegram_id !== telegram_id" :class="player_classes[player.telegram_id]">
      <div class="card back" v-for="n in hand.length">*</div>
    </div>
    <div v-if="player.telegram_id === telegram_id" :class="player_classes[player.telegram_id]">
      {{pass_cards}}
      <ul class="table">
        <li v-for="c in hand" :key="c">
          <label :for="c" :class="classes(c)" v-if="game.waiting_for_pass">
            <span class="rank">{{c.charAt(0)}}</span>
            <span class="suit">{{suitSymbol(c)}}</span>
            <input type="checkbox" :name="c" :id="c" :value="c" v-model="pass_cards" @change="pass_cards_changed" />
          </label>
          <a href="#" :class="classes(c)+isSuitable(c)?['invalid']:[]" v-if="!game.waiting_for_pass">
          <span class="rank">{{c.charAt(0)}}</span+c<span class="suit">{{suitSymbol(c)}}</span>
        </a>
        </li>
      </ul>
<!--      <ul class="hand">-->
<!--        <li v-for="c in hand" :key="c">-->
<!--          <div :class="classes(c)">-->
<!--            <span class="rank">{{c.charAt(0)}}</span><span class="suit">{{suitSymbol(c)}}</span>-->
<!--          </div>-->
<!--        </li>-->
<!--      </ul>-->
      <button v-for="c in hand" @click="$emit('move', c)">{{c}}</button>
    </div>
  </div>
    <div class="mid">
  <p v-for="c in table">{c}</p>
      </div>
  </div>
</template>

<script>
export default {
  name: 'Game',
  props: ['telegram_id', 'game', 'hand', 'waiting_for_pass', 'table'],
  emits: ['chat', 'move', 'pass_cards'],
  data(){
    return {
      pass_cards: []
    }
  },
  methods: {
    classes(card) {
      return ['card', `rank-${card.charAt(0)}`, card.charAt(1)]
    },
    suitSymbol(card) {
      return {'h': '♥', 'd': '♦', 'c': '♣', 's': '♠'}[card.charAt(1)]
    },
    pass_cards_changed() {
      if(this.pass_cards.length === 3) {
        this.$emit('pass_cards', self.pass_cards);
        this.pass_cards = [];
        this.game.waiting_for_pass = false

      }
    },
    isSuitable(card) {
      if(this.table.length == 0) {
        if(this.game.score_opened) return true;
        else return (card === 'qs') || card.charAt(1) === 'h';
      } else {
        let suit = this.table[0].charAt(1);
        if(this.hand.some(c => c.charAt(1)===suit)) return card.charAt(1) === suit;
        return true;
      }
    }
  },
  computed: {
    player_classes() {
      let order=['south', 'west', 'north', 'east', 'south', 'west', 'north', 'east']
      let res = {}
      for(let i=0; i<4; i++){
        if(this.game.players[i].telegram_id === this.telegram_id) {
          order = order.splice(i)
          return Object.fromEntries(this.game.players.map((p, i) => [p.telegram_id, order[i]]))
        }
      }

    }
  },
  mounted() {

  },
}

</script>
<style>
@import "../assets/cards.css";
.south{
  position: absolute;
  bottom: 0;
  width: 80%;
  height: 200px;
  display: block;
  margin-left: auto;
  margin-right: auto;
  background-color: red;
}
.north{
  position: absolute;
  top: 0;
  width: 80%;
  height: 200px;
  display: block;
  margin-left: auto;
  margin-right: auto;
}
.west{
  position: absolute;
  left: 0;
  height: 80%;
  width: 200px;
  display: block;
  margin-top: auto;
  margin-bottom: auto;
}
.west div.card{
  display: block;
  margin-top: -40px;
}
.east{
  position: absolute;
  right: 0;
  height: 80%;
  width: 200px;
  display: block;
  margin-top: auto;
  margin-bottom: auto;
}
.east div.card{
  display: block;
  margin-top: -40px;
}
.mid {
  background: orange;
  width: 300px;
  height: 200px;
  position: absolute;
  top: 50%;
  left: 50%;
  margin: -150px 0 0 -100px;
}
.invalid {
    opacity:0.5;
}
</style>
