const display = document.getElementById("display");
const lyricElement = document.getElementById("lyric");
const musicStatus = document.getElementById("music-status");
const music = document.getElementById("music");
const app = document.getElementById("app");
const buttons = document.querySelectorAll("button");

const lyrics = [];

// Times copied from the Pygame version.
// Put the same number of non-empty lyric lines in lyrics.txt.
// The browser version loads lyrics.txt automatically.
const LYRIC_TIMES = [
  4.0, 6.0, 8.0, 12.0, 14.0, 16.0, 18.0, 21.0,
  24.0, 26.0, 28.0, 32.0, 37.0, 40.0, 56.0, 60.0,
  64.0, 68.0, 72.0, 76.0, 80.0, 84.0, 88.0, 92.0,
  96.0, 100.0, 104.0, 108.0, 112.0, 116.0, 120.0,
  124.0, 128.0, 132.0, 136.0, 140.0, 144.0, 148.0,
  152.0, 156.0, 160.0, 164.0, 168.0, 172.0, 176.0,
  180.0, 184.0, 188.0, 192.0, 196.0, 200.0, 204.0,
  208.0, 212.0, 216.0, 220.0, 224.0, 228.0, 232.0,
  236.0, 240.0
];

let current = "0";
let previous = null;
let operator = null;
let waitingForNumber = false;
let calculatorLocked = false;

async function loadLyrics() {
  try {
    const response = await fetch("lyrics.txt", { cache: "no-store" });
    if (!response.ok) throw new Error("lyrics.txt not found");

    const text = await response.text();

    lyrics.length = 0;
    text.split(/\r?\n/)
      .map(line => line.trim())
      .filter(Boolean)
      .forEach(line => lyrics.push(line));
  } catch (error) {
    console.warn("Could not load lyrics.txt:", error);
  }
}

function formatNumber(value) {
  if (typeof value === "string") return value;

  if (!Number.isFinite(value)) return "Error";

  if (Number.isInteger(value)) {
    return String(value);
  }

  return String(Number(value.toFixed(10)));
}

function calculate(a, b, op) {
  try {
    if (op === "+") return a + b;
    if (op === "−") return a - b;
    if (op === "×") return a * b;

    if (op === "÷") {
      if (b === 0) return "Error";
      return a / b;
    }
  } catch {
    return "Error";
  }

  return "Error";
}

function updateDisplay() {
  display.textContent = current;
}

function startMusic() {
  if (!music.src) return;

  calculatorLocked = true;
  app.classList.add("locked");

  currentLyric = "";
  lyricElement.textContent = "";

  music.currentTime = 0;

  const playPromise = music.play();

  if (playPromise !== undefined) {
    playPromise.catch(error => {
      console.warn("Music could not start:", error);
      calculatorLocked = false;
      app.classList.remove("locked");
    });
  }
}

function stopMusicAndUnlock() {
  music.pause();
  music.currentTime = 0;

  calculatorLocked = false;
  app.classList.remove("locked");

  lyricElement.textContent = "";
}

function updateLyrics() {
  if (!calculatorLocked) return;

  const seconds = music.currentTime;

  let currentLyric = "";

  for (let i = 0; i < LYRIC_TIMES.length; i++) {
    if (i >= lyrics.length) break;

    const start = LYRIC_TIMES[i];
    const end = i + 1 < LYRIC_TIMES.length
      ? LYRIC_TIMES[i + 1]
      : Infinity;

    if (seconds >= start && seconds < end) {
      currentLyric = lyrics[i];
      break;
    }
  }

  lyricElement.textContent = currentLyric;

  // Unlock when the music actually finishes.
  if (music.ended) {
    stopMusicAndUnlock();
  }
}

function pressButton(value) {
  if (calculatorLocked) return;

  // Numbers
  if (/^\d$/.test(value)) {
    if (current === "Error") {
      current = value;
      previous = null;
      operator = null;
      waitingForNumber = false;
      updateDisplay();
      return;
    }

    if (waitingForNumber) {
      current = value;
      waitingForNumber = false;
      updateDisplay();
      return;
    }

    if (current === "0") {
      current = value;
    } else {
      current += value;
    }

    updateDisplay();
    return;
  }

  // Decimal
  if (value === ".") {
    if (current === "Error") {
      current = "0.";
      previous = null;
      operator = null;
      waitingForNumber = false;
    } else if (waitingForNumber) {
      current = "0.";
      waitingForNumber = false;
    } else if (!current.includes(".")) {
      current += ".";
    }

    updateDisplay();
    return;
  }

  // Clear
  if (value === "AC") {
    current = "0";
    previous = null;
    operator = null;
    waitingForNumber = false;
    updateDisplay();
    return;
  }

  // Backspace
  if (value === "⌫") {
    if (current === "Error") {
      current = "0";
    } else if (!waitingForNumber) {
      if (current.length > 1) {
        current = current.slice(0, -1);
      } else {
        current = "0";
      }
    }

    updateDisplay();
    return;
  }

  // Percent
  if (value === "%") {
    if (current === "Error") return;

    const number = Number(current);

    if (!Number.isFinite(number)) {
      current = "Error";
    } else if (previous !== null && ["+", "−"].includes(operator)) {
      current = formatNumber(previous * number / 100);
    } else {
      current = formatNumber(number / 100);
    }

    updateDisplay();
    return;
  }

  // Operators
  if (["+", "−", "×", "÷"].includes(value)) {
    if (current === "Error") return;

    const currentNumber = Number(current);

    if (!Number.isFinite(currentNumber)) {
      current = "Error";
      updateDisplay();
      return;
    }

    if (previous !== null && operator !== null) {
      if (!waitingForNumber) {
        const result = calculate(previous, currentNumber, operator);

        if (result === "Error") {
          current = "Error";
          previous = null;
          operator = null;
          waitingForNumber = false;
          updateDisplay();
          return;
        }

        current = formatNumber(result);
        previous = Number(result);
      }
    } else {
      previous = currentNumber;
    }

    operator = value;
    waitingForNumber = true;

    updateDisplay();
    return;
  }

  // Equals
  if (value === "=") {
    // No pending calculation = play music
    if (previous === null || operator === null) {
      startMusic();
      return;
    }

    try {
      const secondNumber = waitingForNumber
        ? previous
        : Number(current);

      const result = calculate(
        previous,
        secondNumber,
        operator
      );

      current = formatNumber(result);
    } catch {
      current = "Error";
    }

    previous = null;
    operator = null;
    waitingForNumber = true;

    updateDisplay();
  }
}

// Touch/click buttons
buttons.forEach(button => {
  button.addEventListener("click", () => {
    pressButton(button.dataset.value);
  });
});

// Keyboard support
document.addEventListener("keydown", event => {
  if (event.key === "Escape") {
    if (calculatorLocked) {
      stopMusicAndUnlock();
    } else {
      // Don't close the browser; just reset music state.
      return;
    }
    return;
  }

  if (calculatorLocked) return;

  if (/^\d$/.test(event.key)) {
    pressButton(event.key);
    return;
  }

  if (event.key === ".") {
    pressButton(".");
    return;
  }

  if (event.key === "+") {
    pressButton("+");
    return;
  }

  if (event.key === "-") {
    pressButton("−");
    return;
  }

  if (event.key === "*") {
    pressButton("×");
    return;
  }

  if (event.key === "/") {
    event.preventDefault();
    pressButton("÷");
    return;
  }

  if (event.key === "Enter" || event.key === "=") {
    pressButton("=");
    return;
  }

  if (event.key === "Backspace") {
    pressButton("⌫");
    return;
  }

  if (event.key === "%") {
    pressButton("%");
    return;
  }

  if (event.key.toLowerCase() === "c") {
    pressButton("AC");
  }
});

// Keep lyrics synced with the actual audio
music.addEventListener("timeupdate", updateLyrics);

music.addEventListener("ended", () => {
  stopMusicAndUnlock();
});

// Load lyrics immediately
loadLyrics();
updateDisplay();
