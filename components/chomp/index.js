document.addEventListener("DOMContentLoaded", () => {
  const gridDiv = document.getElementById("chomp-grid");

  function renderGrid(data) {
    const n = data.n || 2;
    const m = data.m || 2;
    const available = data.available || [];
    const gameOn = data.game_on !== undefined ? data.game_on : true;
    
    gridDiv.innerHTML = "";
    gridDiv.style.display = "grid";
    gridDiv.style.gridTemplateRows = `repeat(${n}, 1fr)`;
    gridDiv.style.gridTemplateColumns = `repeat(${m}, 1fr)`;

    const availableSet = new Set(available.map(cell => `${cell[0]},${cell[1]}`));
    availableSet.add("0,0");

    for (let i = 0; i < n; i++) {
      for (let j = 0; j < m; j++) {

        const cell = document.createElement("div");
        cell.className = "chomp-cell";
        cell.textContent = (i === 0 && j === 0) ? "☠️" : "🍫";
        cell.setAttribute("data-row", i);
        cell.setAttribute("data-col", j);

        if (i === 0 && j === 0) {
          cell.classList.add("poison");
        }

        const cellKey = `${i},${j}`;
        if (availableSet.has(cellKey)) {
          cell.style.visibility = "visible";
          if (gameOn) {
            cell.classList.remove("disabled");
            cell.addEventListener("click", () => {
              Streamlit.setComponentValue({ row: i, col: j });
            });
          } else {
            cell.classList.add("disabled");
          }
        } else {
          cell.style.visibility = "hidden";
          cell.classList.add("disabled");
        }

        gridDiv.appendChild(cell);
      }
    }
  }

  Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, (event) => {
    renderGrid(event.detail.args.spec);
  const n = event.detail.args.spec.n || 2;
  const frameHeight = 20 + 35 * n + 20;
  Streamlit.setFrameHeight(frameHeight);
  });

  Streamlit.setComponentReady();
});