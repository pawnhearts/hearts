<template>
  <div class="playingCards fourColours rotateHand">
  <h1>game</h1>
  <div v-for="player in game.players">
    {{player.display_name}}
    </div>
    <div class="hand">

      <ul class="hand">
        <li v-for="c in hand" :key="c">
          <label :for="c" :class="classes(c)" v-if="game.waiting_for_pass">
            <span class="rank">{{c.charAt(0)}}</span>
            <span class="suit">{{suitSymbol(c)}}</span>
            <input type="checkbox" :name="c" :id="c" :value="c" v-model="pass_cards" @change="pass_cards_changed" />
          </label>
          <a href="#" :class="classes(c)+isSuitable(c)?['invalid']:[]" v-if="!game.waiting_for_pass">
          <span class="rank">{{c.charAt(0)}}</span><span class="suit">{{suitSymbol(c)}}</span>
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
<!--      <button v-for="c in hand" @click="$emit('move', c)">{{c}}</button>-->
    </div>
    <div :class="['mid', player_classes[i]]" v-for="(card, i) in table" :key="card">
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
      return ['card', `rank-${card.charAt(0)}`, card.charAt(1), this.isSuitable(card)?'':'disabled']
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
          return this.game.players.map((p, i) => order[i])

        }
      }

    }
  },
  mounted() {

  },
}

</script>
<style>
//@import "../assets/cards.css";
div.hand{
  position: absolute;
  bottom: 0;
  width: 100%;
  height: 200px;
  display: block;
  margin-left: auto;
}
.mid {
  width: 3.3em;
  height: 4.6em;
  position: absolute;
  top: 50%;
  left: 50%;
  margin-top: 4.6em;
  background-color: red;
}
div.mid.north{
  margin-top: 4.6em;
}
div.mid.south{
  margin-top: -4.6em;
}
div.mid.west{
  margin-left: -3.3em;
}
div.mid.east{
  margin-left: 3.3em;
}
.invalid {
    opacity:0.5;
}
</style>
