<template>
  <div
    class="playing-card"
    :class="[{ facedown: !faceUp }, colorClass]"
    :style="{ width: width + 'px' }"
    :aria-label="faceUp ? `${rank} of ${suit}` : 'Card face down'"
  >
    <template v-if="faceUp">
      <svg
        class="card-svg"
        :viewBox="`0 0 ${CARD_W} ${CARD_H}`"
        xmlns="http://www.w3.org/2000/svg"
        xmlns:xlink="http://www.w3.org/1999/xlink"
      >
        <use :href="`/svg-cards.svg#${svgId}`" x="0" y="0" />
      </svg>
    </template>

    <template v-else>
      <div class="card-back">
        <div class="back-pattern">
          <span v-for="i in 12" :key="i" class="back-suit">{{ backSuits[i % 4] }}</span>
        </div>
        <div class="back-border" />
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const CARD_W = 169.075
const CARD_H = 244.64

const props = defineProps({
  rank: {
    type: String,
    required: true,
    // "Nine" | "Ten" | "Jack" | "Queen" | "King" | "Ace"
  },
  suit: {
    type: String,
    required: true,
    // "Spades" | "Hearts" | "Clubs" | "Diamonds"
  },
  faceUp: {
    type: Boolean,
    default: true,
  },
  width: {
    type: Number,
    default: 80,
  },
})

// Map from our rank/suit names → svg-cards id format
const RANK_MAP = {
  Nine:  '9',
  Ten:   '10',
  Jack:  'jack',
  Queen: 'queen',
  King:  'king',
  Ace:   'ace',
}

const SUIT_MAP = {
  Spades:   'spade',
  Hearts:   'heart',
  Clubs:    'club',
  Diamonds: 'diamond',
}

const svgId = computed(() => {
  const r = RANK_MAP[props.rank]
  const s = SUIT_MAP[props.suit]
  return `${s}_${r}`
})

const colorClass = computed(() => {
  return ['Hearts', 'Diamonds'].includes(props.suit) ? 'red' : 'black'
})

const backSuits = ['♠', '♥', '♦', '♣']
</script>

<style scoped>
.playing-card {
  display: inline-block;
  position: relative;
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  flex-shrink: 0;
  aspect-ratio: 169 / 244;
  background: #fff;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.card-svg {
  width: 100%;
  height: 100%;
  display: block;
}

/* Face-down card */
.card-back {
  width: 100%;
  height: 100%;
  background: #1a3a5c;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.back-pattern {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: repeat(3, 1fr);
  gap: 2px;
  width: 80%;
  height: 80%;
  opacity: 0.25;
}

.back-suit {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1em;
  color: #fff;
}

.back-border {
  position: absolute;
  inset: 6px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  pointer-events: none;
}

/* Hover lift — only when used interactively (parent adds .interactive) */
.playing-card.interactive {
  cursor: pointer;
}

.playing-card.interactive:hover {
  transform: translateY(-6px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
}

.playing-card.selected {
  transform: translateY(-12px);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.5);
  outline: 2px solid #f0ede6;
  outline-offset: 2px;
}
</style>
