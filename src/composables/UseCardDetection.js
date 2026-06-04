/**
 * useCardDetection.js
 *
 * Composable that handles CV logic for the Vue frontend:
 *   - Captures frames from a video element on an interval
 *   - Sends base64-encoded JPEG to the FastAPI /detect endpoint
 *   - Returns a reactive detectedCard ref
 *
 * Usage:
 *   const { detectedCard, startDetection, stopDetection, isDetecting, error }
 *     = useCardDetection(videoEl)
 */

import { ref } from 'vue'

const API_BASE         = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
const SAMPLE_INTERVAL  = 500    // ms between frame captures
const JPEG_QUALITY     = 0.8    // lower = smaller payload, faster round-trip

export function useCardDetection(videoEl) {
  const detectedCard = ref(null)
  const isDetecting  = ref(false)
  const error        = ref(null)

  let intervalId = null
  const canvas   = document.createElement('canvas')
  const ctx      = canvas.getContext('2d')

  function captureFrame() {
    const video = videoEl.value
    if (!video || video.readyState < 2) return null
    canvas.width  = video.videoWidth
    canvas.height = video.videoHeight
    ctx.save()
    ctx.scale(-1, 1)
    ctx.drawImage(video, -canvas.width, 0)
    ctx.restore()
    return canvas.toDataURL('image/jpeg', JPEG_QUALITY).split(',')[1]
  }

  async function detect() {
    const frame = captureFrame()
    if (!frame) return

    try {
      const response = await fetch(`${API_BASE}/detect`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ frame }),
      })

      if (!response.ok) {
        error.value = `API error: ${response.status}`
        return
      }

      const data = await response.json()

      detectedCard.value = data.card ?? null
      error.value = null

    } catch (err) {
      error.value = err.message
      // Don't log every interval failure — only set the ref
    }
  }

  function startDetection() {
    if (isDetecting.value) return
    isDetecting.value = true
    error.value = null
    intervalId = setInterval(detect, SAMPLE_INTERVAL)
  }

  function stopDetection() {
    clearInterval(intervalId)
    intervalId    = null
    isDetecting.value  = false
    detectedCard.value = null
  }

  return { detectedCard, isDetecting, error, startDetection, stopDetection }
}
