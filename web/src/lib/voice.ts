/** Bangla speech-to-text through the browser's Web Speech API (Chrome: webkitSpeechRecognition). */

type Recognition = {
  lang: string
  interimResults: boolean
  maxAlternatives: number
  onresult: ((e: { results: ArrayLike<ArrayLike<{ transcript: string }>> }) => void) | null
  onerror: ((e: { error: string }) => void) | null
  onend: (() => void) | null
  start: () => void
  stop: () => void
}
type RecognitionCtor = new () => Recognition

function ctor(): RecognitionCtor | null {
  if (typeof window === 'undefined') return null
  const w = window as unknown as { SpeechRecognition?: RecognitionCtor; webkitSpeechRecognition?: RecognitionCtor }
  return w.SpeechRecognition ?? w.webkitSpeechRecognition ?? null
}

export function isVoiceSupported(): boolean {
  return ctor() !== null
}

/** Listen once in Bangla (bn-BD); resolves with the transcript, rejects with an error code. */
export function listenBn(): Promise<string> {
  const C = ctor()
  if (!C) return Promise.reject(new Error('unsupported'))
  return new Promise((resolve, reject) => {
    const r = new C()
    let done = false
    r.lang = 'bn-BD'
    r.interimResults = false
    r.maxAlternatives = 1
    r.onresult = (e) => {
      done = true
      resolve(e.results[0]?.[0]?.transcript ?? '')
    }
    r.onerror = (e) => {
      done = true
      reject(new Error(e.error || 'error'))
    }
    r.onend = () => {
      if (!done) reject(new Error('no-speech'))
    }
    r.start()
  })
}
