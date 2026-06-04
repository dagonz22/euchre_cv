<template>
  <div class="home">
    <div class="hero">
      <div class="suits-bg" aria-hidden="true">
        <span>♠</span><span>♥</span><span>♦</span><span>♣</span>
      </div>

      <div class="logo">
        <span class="logo-suit">♠</span>
        <h1>Euchre</h1>
        <span class="logo-suit red">♥</span>
      </div>
      <p class="tagline">Play with real cards, virtually.</p>

      <div class="actions">
        <button class="btn btn-primary" @click="createLobby">
          Create Lobby
        </button>
        <div class="join-row">
          <input
            v-model="joinCodeInput"
            class="join-input"
            maxlength="4"
            placeholder="Code"
            type="text"
            @keydown.enter="joinLobby"
          />
          <button class="btn btn-secondary" @click="joinLobby" :disabled="joinCodeInput.length < 4">
            Join Lobby
          </button>
        </div>
        <p v-if="joinError" class="join-error">{{ joinError }}</p>
      </div>
    </div>

    <div class="webcam-section">
      <div class="webcam-header">
        <h2>Test Your Webcam</h2>
        <p>Hold a card up to the camera. Once card detection is active, the rank and suit will appear here.</p>
      </div>

      <div class="webcam-container">
        <div class="webcam-feed">
          <video ref="videoEl" autoplay playsinline muted />
          <div v-if="!cameraActive" class="camera-placeholder">
            <span class="camera-icon">⬡</span>
            <p>Camera not active</p>
          </div>
        </div>

        <div class="detection-panel">
          <div class="detection-label">Detected Card</div>
          <div class="detection-result">
            <PlayingCard
              v-if="detectedCard"
              :rank="detectedCard.rank"
              :suit="detectedCard.suit"
              :width="100"
            />
            <span v-else class="no-card">No card detected</span>
          </div>
          <div class="confidence" v-if="detectedCard">
            <div class="confidence-bar">
              <div class="confidence-fill" :style="{ width: detectedCard.confidence + '%' }" />
            </div>
            <span>{{ detectedCard.confidence }}% confidence</span>
          </div>
        </div>
      </div>

      <button class="btn btn-camera" @click="toggleCamera">
        {{ cameraActive ? 'Stop Camera' : 'Start Camera' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import PlayingCard from '@/components/PlayingCard.vue'

const router = useRouter()

const joinCodeInput = ref('')
const joinError = ref('')

const videoEl = ref(null)
const cameraActive = ref(false)
let mediaStream = null

const detectedCard = ref(null)

function generateCode() {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
  return Array.from({ length: 4 }, () => chars[Math.floor(Math.random() * chars.length)]).join('')
}

function createLobby() {
  const code = generateCode()
  router.push(`/lobby/${code}`)
}

function joinLobby() {
  const code = joinCodeInput.value.trim().toUpperCase()
  if (code.length !== 4) return
  joinError.value = ''
  router.push(`/lobby/${code}`)
}

async function toggleCamera() {
  if (cameraActive.value) {
    mediaStream?.getTracks().forEach(t => t.stop())
    mediaStream = null
    cameraActive.value = false
    detectedCard.value = null
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

.home {
  --bg:           #0e0e0f;
  --bg-surface:   #111113;
  --bg-raised:    #16161a;
  --border:       #1e1e20;
  --border-mid:   #2e2e32;
  --border-hover: #4a4a52;
  --text-primary: #f0ede6;
  --text-muted:   #6b6b72;
  --text-dim:     #3a3a40;
  --suit-dim:     #4a4a52;
  --suit-red:     #8b2020;
  --card-red:     #c0392b;
  --green:        #4a7c59;
  --btn-secondary-border: #5a5a64;
  --btn-secondary-text:   #c8c4bc;
}

@media (prefers-color-scheme: light) {
  .home {
    --bg:           #f5f2eb;
    --bg-surface:   #edeae1;
    --bg-raised:    #ffffff;
    --border:       #dedad0;
    --border-mid:   #ccc8be;
    --border-hover: #a8a49c;
    --text-primary: #0e0e0f;
    --text-muted:   #6b6b72;
    --text-dim:     #b0ada6;
    --suit-dim:     #9a9690;
    --suit-red:     #8b2020;
    --card-red:     #c0392b;
    --green:        #3a6647;
    --btn-secondary-border: #ccc8be;
    --btn-secondary-text:   #0e0e0f;
  }
}

* { box-sizing: border-box; margin: 0; padding: 0; }

.home {
  min-height: 100vh;
  background: var(--bg);
  color: var(--text-primary);
  font-family: 'DM Sans', sans-serif;
}

.hero {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 6rem 2rem 5rem;
  overflow: hidden;
  border-bottom: 1px solid var(--border);
}

.suits-bg {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4rem;
  font-size: 14rem;
  opacity: 0.04;
  pointer-events: none;
  user-select: none;
  letter-spacing: -1rem;
}

.logo {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.logo-suit { font-size: 2.5rem; color: var(--suit-dim); }
.logo-suit.red { color: var(--suit-red); }

h1 {
  font-family: 'Playfair Display', serif;
  font-size: 4rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text-primary);
}

.tagline {
  font-size: 1rem;
  color: var(--text-muted);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-weight: 300;
  margin-bottom: 3rem;
}

.actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.875rem;
  width: 100%;
  max-width: 320px;
}

.btn {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.95rem;
  font-weight: 500;
  padding: 0.8rem 2rem;
  border-radius: 4px;
  border: 1px solid transparent;
  cursor: pointer;
  letter-spacing: 0.04em;
  transition: all 0.15s ease;
}

.btn-primary {
  width: 100%;
  background: var(--text-primary);
  color: var(--bg);
  border-color: var(--text-primary);
}

.btn-primary:hover { opacity: 0.88; }

.join-row {
  display: flex;
  gap: 0.5rem;
  width: 100%;
}

.join-input {
  font-family: 'Playfair Display', serif;
  font-size: 1.1rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  width: 90px;
  flex-shrink: 0;
  padding: 0.75rem 0.5rem;
  background: var(--bg-surface);
  border: 1px solid var(--border-mid);
  border-radius: 4px;
  color: var(--text-primary);
  outline: none;
  text-align: center;
  transition: border-color 0.15s;
}

.join-input::placeholder {
  color: var(--text-dim);
  letter-spacing: 0.05em;
  font-size: 0.85rem;
  font-family: 'DM Sans', sans-serif;
  font-weight: 400;
}

.join-input:focus { border-color: var(--text-primary); }

.btn-secondary {
  flex: 1;
  background: transparent;
  color: var(--btn-secondary-text);
  border-color: var(--btn-secondary-border);
}

.btn-secondary:hover:not(:disabled) {
  border-color: var(--border-hover);
  background: var(--bg-surface);
}

.btn-secondary:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.join-error {
  font-size: 0.85rem;
  color: var(--card-red);
  text-align: center;
}

.btn-camera {
  background: transparent;
  color: var(--text-muted);
  border: 1px solid var(--border-mid);
  margin-top: 1.5rem;
  font-size: 0.85rem;
  padding: 0.6rem 1.5rem;
}

.btn-camera:hover { color: var(--text-primary); border-color: var(--border-hover); }

.webcam-section {
  max-width: 860px;
  margin: 0 auto;
  padding: 4rem 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.webcam-header { text-align: center; margin-bottom: 2rem; }

.webcam-header h2 {
  font-family: 'Playfair Display', serif;
  font-size: 1.6rem;
  font-weight: 400;
  margin-bottom: 0.5rem;
  color: var(--text-primary);
}

.webcam-header p { font-size: 0.9rem; color: var(--text-muted); max-width: 480px; }

.webcam-container {
  display: grid;
  grid-template-columns: 1fr 220px;
  gap: 1.5rem;
  width: 100%;
}

.webcam-feed {
  position: relative;
  aspect-ratio: 4/3;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  overflow: hidden;
}

.webcam-feed video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scaleX(-1);
}

.camera-placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
}

.camera-icon { font-size: 3rem; color: var(--border-mid); }
.camera-placeholder p { font-size: 0.85rem; color: var(--text-dim); }

.detection-panel {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 1.25rem;
  background: var(--bg-surface);
}

.detection-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-muted);
}

.detection-result {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
}

.no-card { font-size: 0.85rem; color: var(--text-dim); text-align: center; }

.detected-rank {
  font-family: 'Playfair Display', serif;
  font-size: 3rem;
  font-weight: 700;
  line-height: 1;
  color: var(--text-primary);
}

.detected-suit { font-size: 2.5rem; line-height: 1; }
.detected-suit.red   { color: var(--card-red); }
.detected-suit.black { color: var(--text-primary); }

.detected-name {
  font-size: 0.8rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.confidence { display: flex; flex-direction: column; gap: 0.4rem; }
.confidence span { font-size: 0.75rem; color: var(--text-muted); }

.confidence-bar {
  height: 3px;
  background: var(--border);
  border-radius: 2px;
  overflow: hidden;
}

.confidence-fill {
  height: 100%;
  background: var(--green);
  border-radius: 2px;
  transition: width 0.3s ease;
}

@media (max-width: 640px) {
  h1 { font-size: 2.5rem; }
  .suits-bg { font-size: 8rem; gap: 1rem; }
  .webcam-container { grid-template-columns: 1fr; }
}
</style>
