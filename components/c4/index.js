document.addEventListener("DOMContentLoaded", () => {
  const gridDiv = document.getElementById("connect4-grid");

  function renderGrid(data) {
    const rows = data.rows || 6;
    const cols = data.cols || 7;
    const grid = data.grid || Array(rows).fill().map(() => Array(cols).fill(0));
    const gameOn = data.game_on !== undefined ? data.game_on : true;
    const validColumns = data.valid_columns || [];
    
    gridDiv.innerHTML = "";
    gridDiv.style.display = "grid";
    gridDiv.style.gridTemplateRows = `repeat(${rows}, 1fr)`;
    gridDiv.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;

    const validColSet = new Set(validColumns);

    for (let row = 0; row < rows; row++) {
      for (let col = 0; col < cols; col++) {
        const cell = document.createElement("div");
        cell.className = "connect4-cell";
        cell.setAttribute("data-row", row);
        cell.setAttribute("data-col", col);

        const cellValue = grid[row][col];
        if (cellValue === 1) {
          cell.classList.add("red");
        } else if (cellValue === 2) {
          cell.classList.add("yellow");
        }

        if (gameOn && validColSet.has(col) && cellValue === 0) {
          let isLowestEmptyInColumn = (row === rows - 1) || (grid[row + 1][col] !== 0);
          
          if (isLowestEmptyInColumn) {
            cell.classList.add("highlight");
            cell.addEventListener("click", () => {
              Streamlit.setComponentValue({ column: col });
            });
          } else {
            cell.classList.add("disabled");
          }
        } else if (cellValue === 0) {
          cell.classList.add("disabled");
        }

        gridDiv.appendChild(cell);
      }
    }
  }

  Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, (event) => {
    renderGrid(event.detail.args.spec);
    const rows = event.detail.args.spec.rows || 6;
    const frameHeight = 30 + (44 + 14) * rows + 30;
    Streamlit.setFrameHeight(frameHeight);
  });

  Streamlit.setComponentReady();
});