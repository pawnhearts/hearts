<template>
  <div v-for="player in game.players">
    {{player.telegram_id}}
    <div v-if="player.telegram_id === telegram_id">
      <ul class="table">
        <li v-for="c in hand" :key="c">
        <div :class="['card', 'rank-'+c.charAt(0), c.charAt(1)]">
          <span class="rank">{{c.charAt(0)}}</span><span class="suit">{{suitSymbol(c)}}</span>
        </div>
        </li>
      </ul>
      <button v-for="c in hand" @click="$emit('move', c)">{{c}}</button>
    </div>
  </div>
  <p v-for="c in table">{c}</p>
</template>

<script setup>
import '@/assets/cards.css'
export default {
  name: 'Game',
  props: ['telegram_id', 'game', 'hand'],
  emits: ['chat', 'move', 'pass_cards'],
  data(){
    return {
    }
  },
  methods: {
    suitSymbol(card) {
      return {'h': '♥', 'd': '♦', 'c': '♣', 's': '♠'}[card.charAt(1)]
    }
  },
  mounted() {

  }
}

</script>
