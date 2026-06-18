/* ════════════════════════════════════════════════════════════
   static/audio.js  --  APPROCHE A : Web Speech API
   Transcription vocale directement dans le navigateur.
   Remplit automatiquement le <textarea id="transcription">.
   ════════════════════════════════════════════════════════════ */

// On récupère les éléments de la page
const btnStart   = document.getElementById("btn-start");
const btnStop    = document.getElementById("btn-stop");
const statutSpan = document.getElementById("statut-audio");
const textarea   = document.getElementById("transcription");

// L'API de reconnaissance vocale -- selon le navigateur elle a deux noms possibles
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

// Si le navigateur ne supporte pas l'API, on prévient l'utilisateur
if (!SpeechRecognition) {
    statutSpan.textContent = "⚠️ Reconnaissance vocale non supportée -- utilisez Google Chrome.";
    btnStart.disabled = true;
} else {
    // Création et configuration du moteur de reconnaissance
    const recognition = new SpeechRecognition();
    recognition.lang           = "fr-FR";   // langue : français
    recognition.continuous     = true;      // ne s'arrête pas après une phrase
    recognition.interimResults = true;      // affiche le texte au fur et à mesure

    // Le texte déjà confirmé (les phrases terminées)
    let texteFinal = "";

    // ÉVÉNEMENT : à chaque fois que l'API "entend" quelque chose
    recognition.onresult = function (event) {
        let texteProvisoire = "";
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const morceau = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                texteFinal += morceau + " ";   // phrase terminée -> on la garde
            } else {
                texteProvisoire += morceau;    // phrase en cours -> provisoire
            }
        }
        // On remplit le textarea : texte confirmé + texte en cours
        textarea.value = texteFinal + texteProvisoire;
    };

    recognition.onerror = function (event) {
        statutSpan.textContent = "Erreur micro : " + event.error;
    };

    // BOUTON DÉMARRER
    btnStart.addEventListener("click", function () {
        texteFinal = textarea.value ? textarea.value + " " : "";  // garde le texte existant
        recognition.start();
        statutSpan.textContent = "Enregistrement en cours... parlez.";
        btnStart.disabled = true;
        btnStop.disabled  = false;
    });

    // BOUTON ARRÊTER
    btnStop.addEventListener("click", function () {
        recognition.stop();
        statutSpan.textContent = "Enregistrement terminé. Vous pouvez corriger le texte.";
        btnStart.disabled = false;
        btnStop.disabled  = true;
    });
}