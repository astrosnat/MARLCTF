(function () {
  const canvas = document.getElementById("replay-canvas");
  const ctx = canvas.getContext("2d");
  const statusText = document.getElementById("viewer-status");
  const artifactLabel = document.getElementById("artifact-label");
  const stepText = document.getElementById("step-text");
  const scoreText = document.getElementById("score-text");
  const terminalText = document.getElementById("terminal-text");
  const eventList = document.getElementById("event-list");
  const scrubber = document.getElementById("step-scrubber");
  const speedSelect = document.getElementById("speed-select");
  const fileInput = document.getElementById("replay-file");

  const state = {
    snapshots: [],
    selectedIndex: 0,
    timer: null,
    speed: 1,
    manifest: null,
  };

  document.getElementById("restart-button").addEventListener("click", () => setIndex(0));
  document.getElementById("step-back-button").addEventListener("click", () => setIndex(state.selectedIndex - 1));
  document.getElementById("step-forward-button").addEventListener("click", () => setIndex(state.selectedIndex + 1));
  document.getElementById("play-button").addEventListener("click", play);
  document.getElementById("pause-button").addEventListener("click", pause);
  speedSelect.addEventListener("change", () => {
    state.speed = Number(speedSelect.value) || 1;
    if (state.timer) {
      pause();
      play();
    }
  });
  scrubber.addEventListener("input", () => setIndex(Number(scrubber.value)));
  fileInput.addEventListener("change", loadSelectedFile);

  fetchArtifact();

  function fetchArtifact() {
    fetch("/api/artifact", { cache: "no-store" })
      .then((response) => response.ok ? response.json() : Promise.reject(new Error("artifact request failed")))
      .then((payload) => {
        state.manifest = payload.manifest;
        if (payload.error) {
          setStatus(payload.error);
          return;
        }
        if (!payload.replay || !payload.replay.snapshots || payload.replay.snapshots.length === 0) {
          setStatus("No replay snapshots loaded");
          drawEmptyBoard();
          return;
        }
        if (!payload.replay.validation.ok) {
          setStatus(payload.replay.validation.errors.join("; "));
        } else {
          setStatus("Replay loaded");
        }
        artifactLabel.textContent = payload.manifest ? payload.manifest.source_path : "Server artifact";
        loadSnapshots(payload.replay.snapshots);
      })
      .catch(() => {
        setStatus("No server artifact loaded");
        drawEmptyBoard();
      });
  }

  function loadSelectedFile() {
    const file = fileInput.files && fileInput.files[0];
    if (!file) {
      return;
    }
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const snapshots = String(reader.result)
          .split(/\r?\n/)
          .filter((line) => line.trim().length > 0)
          .map((line) => JSON.parse(line));
        artifactLabel.textContent = file.name;
        setStatus("Replay loaded");
        loadSnapshots(snapshots);
      } catch (error) {
        setStatus("Could not parse replay file");
      }
    };
    reader.readAsText(file);
  }

  function loadSnapshots(snapshots) {
    state.snapshots = snapshots;
    state.selectedIndex = 0;
    scrubber.min = "0";
    scrubber.max = String(Math.max(0, snapshots.length - 1));
    scrubber.value = "0";
    renderSnapshot();
  }

  function play() {
    if (state.timer || state.snapshots.length <= 1) {
      return;
    }
    state.timer = window.setInterval(() => {
      if (state.selectedIndex >= state.snapshots.length - 1) {
        pause();
        return;
      }
      setIndex(state.selectedIndex + 1);
    }, Math.max(80, 500 / state.speed));
  }

  function pause() {
    if (state.timer) {
      window.clearInterval(state.timer);
      state.timer = null;
    }
  }

  function setIndex(index) {
    if (!state.snapshots.length) {
      return;
    }
    state.selectedIndex = Math.min(Math.max(0, index), state.snapshots.length - 1);
    scrubber.value = String(state.selectedIndex);
    renderSnapshot();
  }

  function renderSnapshot() {
    const snapshot = state.snapshots[state.selectedIndex];
    if (!snapshot) {
      drawEmptyBoard();
      return;
    }
    drawBoard(snapshot);
    const score = snapshot.score || { red: 0, blue: 0 };
    const terminal = snapshot.terminal || {};
    stepText.textContent = `Step ${snapshot.step} / ${state.snapshots[state.snapshots.length - 1].step}`;
    scoreText.textContent = `Red ${score.red || 0} - Blue ${score.blue || 0}`;
    terminalText.textContent = terminal.reason
      ? `${terminal.status}: ${terminal.winner || "draw"} (${terminal.reason})`
      : `${terminal.status || "running"}`;
    renderEvents(snapshot.events || []);
  }

  function drawBoard(snapshot) {
    const map = snapshot.map;
    const width = canvas.width;
    const height = canvas.height;
    const cell = Math.floor(Math.min(width / map.width, height / map.height));
    const offsetX = Math.floor((width - cell * map.width) / 2);
    const offsetY = Math.floor((height - cell * map.height) / 2);

    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = "#f8faf7";
    ctx.fillRect(0, 0, width, height);

    for (let y = 0; y < map.height; y += 1) {
      for (let x = 0; x < map.width; x += 1) {
        ctx.fillStyle = (x + y) % 2 === 0 ? "#eef3ea" : "#e6eee2";
        ctx.fillRect(offsetX + x * cell, offsetY + y * cell, cell, cell);
        ctx.strokeStyle = "#c8d2c2";
        ctx.strokeRect(offsetX + x * cell, offsetY + y * cell, cell, cell);
      }
    }

    (map.walls || []).forEach(([x, y]) => {
      ctx.fillStyle = "#3d4a3b";
      ctx.fillRect(offsetX + x * cell, offsetY + y * cell, cell, cell);
    });

    drawFlags(snapshot.flags || {}, cell, offsetX, offsetY);
    drawAgents(snapshot.agents || {}, cell, offsetX, offsetY);
  }

  function drawFlags(flags, cell, offsetX, offsetY) {
    Object.entries(flags).forEach(([team, flag]) => {
      if (flag.x === null || flag.y === null || flag.x === undefined || flag.y === undefined) {
        return;
      }
      const cx = offsetX + flag.x * cell + cell / 2;
      const cy = offsetY + flag.y * cell + cell / 2;
      ctx.fillStyle = team === "red" ? "#d83b3b" : "#2f67d8";
      ctx.beginPath();
      ctx.moveTo(cx - cell * 0.18, cy + cell * 0.22);
      ctx.lineTo(cx - cell * 0.18, cy - cell * 0.25);
      ctx.lineTo(cx + cell * 0.24, cy - cell * 0.08);
      ctx.lineTo(cx - cell * 0.18, cy + cell * 0.08);
      ctx.closePath();
      ctx.fill();
    });
  }

  function drawAgents(agents, cell, offsetX, offsetY) {
    Object.entries(agents).forEach(([agentId, agent]) => {
      const cx = offsetX + agent.x * cell + cell / 2;
      const cy = offsetY + agent.y * cell + cell / 2;
      ctx.fillStyle = agent.team === "red" ? "#f05b5b" : "#4f83f1";
      ctx.strokeStyle = agent.has_flag ? "#111827" : "#ffffff";
      ctx.lineWidth = Math.max(2, Math.floor(cell * 0.06));
      ctx.beginPath();
      ctx.arc(cx, cy, cell * 0.28, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
      ctx.fillStyle = "#111827";
      ctx.font = `${Math.max(10, Math.floor(cell * 0.2))}px system-ui, sans-serif`;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(agentId.split("_")[1], cx, cy);
    });
  }

  function renderEvents(events) {
    eventList.replaceChildren();
    if (!events.length) {
      const item = document.createElement("li");
      item.textContent = "None";
      eventList.appendChild(item);
      return;
    }
    events.forEach((event) => {
      const item = document.createElement("li");
      const details = event.details ? ` ${JSON.stringify(event.details)}` : "";
      item.textContent = `${event.step}: ${event.event_type}${event.agent_id ? ` ${event.agent_id}` : ""}${details}`;
      eventList.appendChild(item);
    });
  }

  function drawEmptyBoard() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#f8faf7";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#4b5563";
    ctx.font = "16px system-ui, sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("No replay", canvas.width / 2, canvas.height / 2);
  }

  function setStatus(message) {
    statusText.textContent = message;
    statusText.dataset.ready = message.toLowerCase().includes("loaded") ? "true" : "false";
  }
})();