// Suraksha Setu v4 — voice alert (speech synthesis) + voice input (speech recognition).

export function speakText(text){
  if(text && 'speechSynthesis' in window){
    const u = new SpeechSynthesisUtterance(text);
    u.lang = 'hi-IN';
    speechSynthesis.speak(u);
    return true;
  }
  return false;
}

export function startVoiceInput(onText){
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if(!SR) return false;
  const r = new SR();
  r.lang = 'hi-IN';
  r.onresult = e => onText(e.results[0][0].transcript);
  r.start();
  return true;
}
