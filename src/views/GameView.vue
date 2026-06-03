<template>
  <div class="game">
    <nav class="nav">
      <span class="nav-title">Euchre</span>
      <span class="nav-code">{{ code }}</span>
      <div class="nav-scores">
        <span class="score-item">Team A <strong>{{ scores[0] }}</strong></span>
        <span class="score-sep">·</span>
        <span class="score-item">Team B <strong>{{ scores[1] }}</strong></span>
      </div>
    </nav>

    <div class="game-content">
      <div class="table-area">
        <div class="trick-zone">
          <p class="zone-label">Current Trick</p>
          <div class="played-cards">
            <div
              v-for="(play, i) in currentTrick"
              :key="i"
              class="played-card"
              :class="play.color"
            >
              <span class="card-rank">{{ play.rank }}</span>
              <span class="card-suit-sym">{{ play.suitSymbol }}</span>
            </div>
            <div
              v-for="i in (4 - currentTrick.length)"
              :key="'empty-' + i"
              class="played-card empty"
            />
          </div>
        </div>

        <div class="game-info">
          <div class="info-row" v-if="trump">
            <span class="info-label">Trump</span>
            <span class="info-value" :class="trumpColor">{{ trumpSymbol }} {{ trump }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Tricks</span>
            <span class="info-value">A: {{ tricks[0] }} · B: {{ tricks[1] }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Dealer</span>
            <span class="info-value">{{ players[dealer] }}</span>
          </div>
        </div>
      </div>

      <div class="hand-area">
        <div class="hand-header">
          <span class="hand-label">Your Hand</span>
          <span class="hand-hint" v-if="isYourTurn">— your turn to play</span>
        </div>
        <div class="hand-cards">
          <div
            v-for="(card, i) in hand"
            :key="i"
            class="hand-card"
            :class="[card.color, { 'your-turn': isYourTurn, selected: selectedCard === i }]"
            @click="selectCard(i)"
          >
            <span class="card-rank">{{ card.rank }}</span>
            <span class="card-suit-sym">{{ card.suitSymbol }}</span>
          </div>
        </div>

        <button
          v-if="selectedCard !== null"
          class="btn btn-play"
          @click="playCard"
        >
          Play {{ hand[selectedCard]?.rank }} {{ hand[selectedCard]?.suitSymbol }}
        </button>
      </div>

      <div class="webcam-strip">
        <div class="webcam-mini">
          <video ref="videoEl" autoplay playsinline muted />
          <div v-if="!cameraActive" class="cam-off">
            <span>Camera off</span>
          </div>
        </div>
        <div class="cam-detection">
          <span class="cam-label">Detected</span>
          <span class="cam-result" :class="{ active: detectedCard }">
            {{ detectedCard ? `${detectedCard.rank} ${detectedCard.suitSymbol}` : '—' }}
          </span>
        </div>
        <button class="btn-cam-toggle" @click="toggleCamera">
          {{ cameraActive ? 'Stop' : 'Start' }} Camera
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const code = route.params.code

const scores = ref([0, 0])
const tricks = ref([0, 0])
const dealer = ref(0)
const trump = ref(null)
const players = ref(['You', 'Player 2', 'Player 3', 'Player 4'])
const isYourTurn = ref(false)
const selectedCard = ref(null)
const currentTrick = ref([])
const detectedCard = ref(null)

const hand = ref([])

const trumpColor = computed(() => {
  if (!trump.value) return ''
  return ['Hearts', 'Diamonds'].includes(trump.value) ? 'red' : 'black'
})

const trumpSymbol = computed(() => {
  const symbols = { Spades: '♠', Hearts: '♥', Clubs: '♣', Diamonds: '♦' }
  return symbols[trump.value] ?? ''
})

function selectCard(i) {
  if (!isYourTurn.value) return
  selectedCard.value = selectedCard.value === i ? null : i
}

function playCard() {
  if (selectedCard.value === null) return
  // CV / game logic will hook in here
  selectedCard.value = null
}

const videoEl = ref(null)
const cameraActive = ref(false)
let mediaStream = null

async function toggleCamera() {
  if (cameraActive.value) {
    mediaStream?.getTracks().forEach(t => t.stop())
    mediaStream = null
    cameraActive.value = false
    return
  }
  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
    videoEl.value.srcObject = mediaStream
    cameraActive.value = true
  } catch (err) {
    console.error('Camera error:', err)
  }
}

onUnmounted(() => {
  mediaStream?.getTracks().forEach(t => t.stop())
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap');

.game {
  --bg:           #0e0e0f;
  --bg-surface:   #111113;
  --bg-raised:    #16161a;
  --border:       #1e1e20;
  --border-mid:   #2e2e32;
  --border-hover: #4a4a52;
  --text-primary: #f0ede6;
  --text-muted:   #6b6b72;
  --text-dim:     #3a3a40;
  --red:          #c0392b;
  --green:        #4a7c59;
  --highlight:    #2a3a2e;
}

@media (prefers-color-scheme: light) {
  .game {
    --bg:           #f5f2eb;
    --bg-surface:   #edeae1;
    --bg-raised:    #ffffff;
    --border:       #dedad0;
    --border-mid:   #ccc8be;
    --border-hover: #a8a49c;
    --text-primary: #0e0e0f;
    --text-muted:   #6b6b72;
    --text-dim:     #b0ada6;
    --red:          #c0392b;
    --green:        #3a6647;
    --highlight:    #d4eadb;
  }
}

* { box-sizing: border-box; margin: 0; padding: 0; }

.game {
  min-height: 100vh;
  background: var(--bg);
  color: var(--text-primary);
  font-family: 'DM Sans', sans-serif;
  display: flex;
  flex-direction: column;
}

.nav {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 2rem;
  border-bottom: 1px solid var(--border);
  flex-wrap: wrap;
}

.nav-title {
  font-family: 'Playfair Display', serif;
  font-size: 1.1rem;
}

.nav-code {
  font-size: 0.75rem;
  letter-spacing: 0.1em;
  color: var(--text-muted);
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 0.2rem 0.6rem;
}

.nav-scores {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.score-item strong { font-weight: 500; }
.score-sep { color: var(--text-dim); }

.game-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  max-width: 860px;
  margin: 0 auto;
  width: 100%;
  padding: 1.5rem 2rem;
  gap: 1.5rem;
}

.table-area {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 1.5rem;
  align-items: start;
}

.trick-zone {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1.25rem;
}

.zone-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-muted);
  margin-bottom: 1rem;
}

.played-cards {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.played-card {
  width: 60px;
  height: 84px;
  border: 1px solid var(--border-mid);
  border-radius: 6px;
  background: var(--bg-raised);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.15rem;
}

.played-card.empty {
  border-style: dashed;
  border-color: var(--border);
  background: transparent;
}

.played-card.red .card-suit-sym { color: var(--red); }

.card-rank {
  font-family: 'Playfair Display', serif;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
}

.card-suit-sym {
  font-size: 1.2rem;
  line-height: 1;
  color: var(--text-primary);
}

.game-info {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  min-width: 140px;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1.25rem;
}

.info-row { display: flex; flex-direction: column; gap: 0.15rem; }

.info-label {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
}

.info-value {
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--text-primary);
}

.info-value.red { color: var(--red); }

.hand-area {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1.25rem;
}

.hand-header {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.hand-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-muted);
}

.hand-hint {
  font-size: 0.8rem;
  color: var(--green);
}

.hand-cards {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.hand-card {
  width: 64px;
  height: 90px;
  border: 1px solid var(--border-mid);
  border-radius: 6px;
  background: var(--bg-raised);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.2rem;
  transition: all 0.15s;
  user-select: none;
}

.hand-card.your-turn {
  cursor: pointer;
}

.hand-card.your-turn:hover {
  border-color: var(--border-hover);
  transform: translateY(-4px);
}

.hand-card.selected {
  border-color: var(--text-primary);
  transform: translateY(-8px);
  background: var(--highlight);
}

.hand-card.red .card-suit-sym { color: var(--red); }

.btn-play {
  margin-top: 1rem;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.95rem;
  font-weight: 500;
  padding: 0.7rem 2rem;
  border-radius: 4px;
  border: 1px solid var(--text-primary);
  background: var(--text-primary);
  color: var(--bg);
  cursor: pointer;
  transition: opacity 0.15s;
}

.btn-play:hover { opacity: 0.88; }

.webcam-strip {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.875rem 1.25rem;
}

.webcam-mini {
  position: relative;
  width: 80px;
  height: 60px;
  border-radius: 4px;
  overflow: hidden;
  background: var(--bg-raised);
  border: 1px solid var(--border);
  flex-shrink: 0;
}

.webcam-mini video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scaleX(-1);
}

.cam-off {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.65rem;
  color: var(--text-dim);
}

.cam-detection {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  flex: 1;
}

.cam-label {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
}

.cam-result {
  font-family: 'Playfair Display', serif;
  font-size: 1.1rem;
  color: var(--text-dim);
}

.cam-result.active { color: var(--text-primary); }

.btn-cam-toggle {
  background: none;
  border: 1px solid var(--border-mid);
  color: var(--text-muted);
  font-family: 'DM Sans', sans-serif;
  font-size: 0.8rem;
  padding: 0.4rem 0.875rem;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
}

.btn-cam-toggle:hover { color: var(--text-primary); border-color: var(--border-hover); }

@media (max-width: 640px) {
  .table-area { grid-template-columns: 1fr; }
  .game-info { flex-direction: row; flex-wrap: wrap; gap: 1rem; }
}
</style>
