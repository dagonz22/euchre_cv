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
        <button class="btn btn-secondary" @click="showJoinModal = true">
          Join Lobby
        </button>
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
          <div class="detection-result" :class="{ active: detectedCard }">
            <template v-if="detectedCard">
              <span class="detected-rank">{{ detectedCard.rank }}</span>
              <span class="detected-suit" :class="detectedCard.color">{{ detectedCard.suitSymbol }}</span>
              <span class="detected-name">{{ detectedCard.suit }}</span>
            </template>
            <template v-else>
              <span class="no-card">No card detected</span>
            </template>
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

    <Teleport to="body">
      <div v-if="showJoinModal" class="modal-backdrop" @click.self="showJoinModal = false">
        <div class="modal">
          <button class="modal-close" @click="showJoinModal = false" aria-label="Close">✕</button>
          <h2>Join a Lobby</h2>
          <p>Enter the 4-character code from your host.</p>
          <div class="code-inputs">
            <input
              v-for="i in 4"
              :key="i"
              :ref="el => { if (el) codeInputs[i-1] = el }"
              class="code-char"
              maxlength="1"
              type="text"
              @input="onCodeInput($event, i - 1)"
              @keydown.backspace="onCodeBackspace($event, i - 1)"
              @paste.prevent="onCodePaste($event)"
            />
          </div>
          <button
            class="btn btn-primary"
            :disabled="joinCode.length < 4"
            @click="joinLobby"
          >
            Join
          </button>
          <p v-if="joinError" class="join-error">{{ joinError }}</p>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const showJoinModal = ref(false)
const codeInputs = ref([])
const codeChars = ref(['', '', '', ''])
const joinError = ref('')
const joinCode = computed(() => codeChars.value.join(''))

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
  const code = joinCode.value.toUpperCase()
  if (code.length !== 4) return
  joinError.value = ''
  router.push(`/lobby/${code}`)
}

function onCodeInput(e, index) {
  const val = e.target.value.replace(/[^a-zA-Z0-9]/g, '').toUpperCase()
  e.target.value = val.slice(-1)
  codeChars.value[index] = e.target.value
  if (e.target.value && index < 3) {
    codeInputs.value[index + 1]?.focus()
  }
}

function onCodeBackspace(e, index) {
  if (!codeChars.value[index] && index > 0) {
    codeChars.value[index - 1] = ''
    codeInputs.value[index - 1].value = ''
    codeInputs.value[index - 1]?.focus()
  }
}

function onCodePaste(e) {
  const text = e.clipboardData.getData('text').replace(/[^a-zA-Z0-9]/g, '').toUpperCase().slice(0, 4)
  text.split('').forEach((char, i) => {
    codeChars.value[i] = char
    if (codeInputs.value[i]) codeInputs.value[i].value = char
  })
  codeInputs.value[Math.min(text.length, 3)]?.focus()
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
  --bg:          #0e0e0f;
  --bg-surface:  #111113;
  --bg-raised:   #16161a;
  --border:      #1e1e20;
  --border-mid:  #2e2e32;
  --border-hover:#4a4a52;
  --text-primary:#f0ede6;
  --text-muted:  #6b6b72;
  --text-dim:    #3a3a40;
  --suit-dim:    #4a4a52;
  --suit-red:    #8b2020;
  --card-red:    #c0392b;
  --green:       #4a7c59;
}

@media (prefers-color-scheme: light) {
  .home {
    --bg:          #f5f2eb;
    --bg-surface:  #edeae1;
    --bg-raised:   #ffffff;
    --border:      #dedad0;
    --border-mid:  #ccc8be;
    --border-hover:#a8a49c;
    --text-primary:#0e0e0f;
    --text-muted:  #6b6b72;
    --text-dim:    #b0ada6;
    --suit-dim:    #9a9690;
    --suit-red:    #8b2020;
    --card-red:    #c0392b;
    --green:       #3a6647;
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

.logo-suit {
  font-size: 2.5rem;
  color: var(--suit-dim);
}

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
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: center;
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
  background: var(--text-primary);
  color: var(--bg);
  border-color: var(--text-primary);
}

.btn-primary:hover { opacity: 0.88; }
.btn-primary:disabled { opacity: 0.4; cursor: not-allowed; }

.btn-secondary {
  background: transparent;
  color: var(--text-primary);
  border-color: var(--border-mid);
}

.btn-secondary:hover { border-color: var(--border-hover); background: var(--bg-surface); }

.btn-camera {
  background: transparent;
  color: var(--text-muted);
  border-color: var(--border-mid);
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

.webcam-header {
  text-align: center;
  margin-bottom: 2rem;
}

.webcam-header h2 {
  font-family: 'Playfair Display', serif;
  font-size: 1.6rem;
  font-weight: 400;
  margin-bottom: 0.5rem;
  color: var(--text-primary);
}

.webcam-header p {
  font-size: 0.9rem;
  color: var(--text-muted);
  max-width: 480px;
}

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
  color: var(--border-mid);
}

.camera-icon { font-size: 3rem; }
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

.no-card {
  font-size: 0.85rem;
  color: var(--text-dim);
  text-align: center;
}

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

.confidence {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

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

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
}

.modal {
  background: var(--bg-raised);
  border: 1px solid var(--border-mid);
  border-radius: 8px;
  padding: 2.5rem;
  width: 360px;
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: center;
}

.modal h2 {
  font-family: 'Playfair Display', serif;
  font-size: 1.5rem;
  font-weight: 400;
  color: var(--text-primary);
}

.modal p {
  font-size: 0.875rem;
  color: var(--text-muted);
  text-align: center;
}

.modal-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 1rem;
  cursor: pointer;
  padding: 0.25rem;
  line-height: 1;
}

.modal-close:hover { color: var(--text-primary); }

.code-inputs { display: flex; gap: 0.75rem; }

.code-char {
  width: 56px;
  height: 64px;
  text-align: center;
  font-family: 'Playfair Display', serif;
  font-size: 1.75rem;
  font-weight: 700;
  background: var(--bg);
  border: 1px solid var(--border-mid);
  border-radius: 4px;
  color: var(--text-primary);
  outline: none;
  text-transform: uppercase;
  transition: border-color 0.15s;
}

.code-char:focus { border-color: var(--text-primary); }

.join-error { color: var(--card-red); font-size: 0.85rem; }

@media (max-width: 640px) {
  h1 { font-size: 2.5rem; }
  .suits-bg { font-size: 8rem; gap: 1rem; }
  .webcam-container { grid-template-columns: 1fr; }
  .detection-panel { flex-direction: row; flex-wrap: wrap; }
}
</style>
