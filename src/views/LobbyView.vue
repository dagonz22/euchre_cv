<template>
  <div class="lobby">
    <nav class="nav">
      <button class="btn-back" @click="router.push('/')">← Back</button>
      <span class="nav-title">Euchre</span>
    </nav>

    <div class="lobby-content">
      <div class="lobby-header">
        <p class="lobby-label">Lobby Code</p>
        <div class="code-display">
          <span class="code-text">{{ code }}</span>
          <button class="btn-copy" @click="copyCode" :title="copied ? 'Copied!' : 'Copy code'">
            {{ copied ? '✓' : '⧉' }}
          </button>
        </div>
        <p class="lobby-hint">Share this code with up to 3 friends</p>
      </div>

      <div class="players-grid">
        <div
          v-for="seat in 4"
          :key="seat"
          class="player-slot"
          :class="{ filled: players[seat - 1] }"
        >
          <template v-if="players[seat - 1]">
            <div class="player-avatar">{{ players[seat - 1].name[0].toUpperCase() }}</div>
            <div class="player-info">
              <span class="player-name">{{ players[seat - 1].name }}</span>
              <span class="player-tag" :class="players[seat - 1].isHost ? 'host' : 'ready'">
                {{ players[seat - 1].isHost ? 'Host' : 'Ready' }}
              </span>
            </div>
          </template>
          <template v-else>
            <div class="player-avatar empty">{{ seat }}</div>
            <span class="player-waiting">Waiting...</span>
          </template>
        </div>
      </div>

      <div class="teams-preview">
        <div class="team">
          <span class="team-label">Team A</span>
          <span class="team-seats">Seats 1 &amp; 3</span>
        </div>
        <span class="team-vs">vs</span>
        <div class="team">
          <span class="team-label">Team B</span>
          <span class="team-seats">Seats 2 &amp; 4</span>
        </div>
      </div>

      <button
        class="btn btn-primary btn-start"
        :disabled="players.filter(Boolean).length < 4"
        @click="startGame"
      >
        {{ players.filter(Boolean).length < 4 ? `Waiting for ${4 - players.filter(Boolean).length} more player${4 - players.filter(Boolean).length === 1 ? '' : 's'}` : 'Start Game' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const code = route.params.code
const copied = ref(false)

const players = ref([
  { name: 'You', isHost: true },
  null,
  null,
  null,
])

function copyCode() {
  navigator.clipboard.writeText(code)
  copied.value = true
  setTimeout(() => copied.value = false, 2000)
}

function startGame() {
  router.push(`/game/${code}`)
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap');

.lobby {
  --bg:           #0e0e0f;
  --bg-surface:   #111113;
  --bg-raised:    #16161a;
  --border:       #1e1e20;
  --border-mid:   #2e2e32;
  --border-hover: #4a4a52;
  --text-primary: #f0ede6;
  --text-muted:   #6b6b72;
  --text-dim:     #3a3a40;
  --green:        #4a7c59;
  --green-dim:    #1e3326;
  --amber:        #8b6914;
  --amber-dim:    #2e2208;
}

@media (prefers-color-scheme: light) {
  .lobby {
    --bg:           #f5f2eb;
    --bg-surface:   #edeae1;
    --bg-raised:    #ffffff;
    --border:       #dedad0;
    --border-mid:   #ccc8be;
    --border-hover: #a8a49c;
    --text-primary: #0e0e0f;
    --text-muted:   #6b6b72;
    --text-dim:     #b0ada6;
    --green:        #3a6647;
    --green-dim:    #d4eadb;
    --amber:        #8b6914;
    --amber-dim:    #fdf3d8;
  }
}

* { box-sizing: border-box; margin: 0; padding: 0; }

.lobby {
  min-height: 100vh;
  background: var(--bg);
  color: var(--text-primary);
  font-family: 'DM Sans', sans-serif;
}

.nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 2rem;
  border-bottom: 1px solid var(--border);
}

.btn-back {
  background: none;
  border: none;
  color: var(--text-muted);
  font-family: 'DM Sans', sans-serif;
  font-size: 0.9rem;
  cursor: pointer;
  padding: 0;
  transition: color 0.15s;
}

.btn-back:hover { color: var(--text-primary); }

.nav-title {
  font-family: 'Playfair Display', serif;
  font-size: 1.1rem;
  color: var(--text-primary);
}

.lobby-content {
  max-width: 560px;
  margin: 0 auto;
  padding: 3rem 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2.5rem;
}

.lobby-header { text-align: center; display: flex; flex-direction: column; align-items: center; gap: 0.5rem; }

.lobby-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-muted);
}

.code-display {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.code-text {
  font-family: 'Playfair Display', serif;
  font-size: 3.5rem;
  font-weight: 700;
  letter-spacing: 0.15em;
  color: var(--text-primary);
}

.btn-copy {
  background: none;
  border: 1px solid var(--border-mid);
  color: var(--text-muted);
  border-radius: 4px;
  padding: 0.4rem 0.6rem;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-copy:hover { color: var(--text-primary); border-color: var(--border-hover); }

.lobby-hint { font-size: 0.85rem; color: var(--text-muted); }

.players-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  width: 100%;
}

.player-slot {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  padding: 1rem 1.25rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg-surface);
  transition: border-color 0.15s;
}

.player-slot.filled { border-color: var(--border-mid); }

.player-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--border-mid);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 500;
  font-size: 0.95rem;
  color: var(--text-muted);
  flex-shrink: 0;
}

.player-slot.filled .player-avatar {
  background: var(--green-dim);
  color: var(--green);
}

.player-avatar.empty { background: var(--bg-raised); }

.player-info { display: flex; flex-direction: column; gap: 0.2rem; min-width: 0; }

.player-name {
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.player-tag {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 0.15rem 0.5rem;
  border-radius: 3px;
  width: fit-content;
}

.player-tag.host { background: var(--amber-dim); color: var(--amber); }
.player-tag.ready { background: var(--green-dim); color: var(--green); }

.player-waiting { font-size: 0.85rem; color: var(--text-dim); }

.teams-preview {
  display: flex;
  align-items: center;
  gap: 2rem;
  padding: 1rem 2rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg-surface);
  width: 100%;
  justify-content: center;
}

.team { display: flex; flex-direction: column; align-items: center; gap: 0.2rem; }

.team-label {
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.team-seats { font-size: 0.75rem; color: var(--text-muted); }

.team-vs {
  font-family: 'Playfair Display', serif;
  font-size: 1.1rem;
  color: var(--text-dim);
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

.btn-primary:hover:not(:disabled) { opacity: 0.88; }

.btn-primary:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.btn-start { width: 100%; padding: 1rem; font-size: 1rem; }
</style>
