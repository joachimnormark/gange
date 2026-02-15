import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Interaktivt Gitter", layout="wide")

st.title("📐 Interaktivt Rektangel på 10×10 Gitter")
st.markdown("""
**Instruktioner:** 
- Træk i de fire hjørnepunkter for at ændre størrelsen på rektanglet
- Fungerer både med mus og touch
- Sidelængder vises på siderne
- Areal vises i midten
""")

# HTML og JavaScript komponent
html_code = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body {
            margin: 0;
            padding: 20px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: #f0f2f6;
            touch-action: none;
        }
        #container {
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            padding: 20px;
        }
        svg {
            border: 2px solid #ddd;
            border-radius: 5px;
            background: white;
            cursor: default;
            touch-action: none;
        }
        .grid-line {
            stroke: #e0e0e0;
            stroke-width: 1;
        }
        .rectangle {
            fill: #FAF5C0;
            stroke: #FAF5C0;
            stroke-width: 3;
        }
        .corner {
            fill: #4285f4;
            stroke: white;
            stroke-width: 2;
            cursor: pointer;
            transition: r 0.1s;
        }
        .corner:hover {
            fill: #1a73e8;
        }
        .corner.dragging {
            fill: #1a73e8;
            r: 10;
        }
        .dimension-text {
            font-size: 16px;
            font-weight: bold;
            fill: #333;
            text-anchor: middle;
            pointer-events: none;
            user-select: none;
        }
        .area-text {
            font-size: 20px;
            font-weight: bold;
            fill: #4285f4;
            text-anchor: middle;
            pointer-events: none;
            user-select: none;
        }
    </style>
</head>
<body>
    <div id="container">
        <svg id="canvas" width="600" height="600"></svg>
    </div>

    <script>
        const SVG_SIZE = 600;
        const GRID_SIZE = 10;
        const CELL_SIZE = SVG_SIZE / GRID_SIZE;
        
        // State
        let rectangle = {
            x1: 2, y1: 2,  // Top-left
            x2: 7, y2: 7   // Bottom-right (5×5 kvadrat)
        };
        
        let dragState = {
            isDragging: false,
            corner: null,
            startX: 0,
            startY: 0
        };

        // Initialize SVG
        const svg = document.getElementById('canvas');
        
        // Draw grid
        function drawGrid() {
            for (let i = 0; i <= GRID_SIZE; i++) {
                // Vertical lines
                const vLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                vLine.setAttribute('class', 'grid-line');
                vLine.setAttribute('x1', i * CELL_SIZE);
                vLine.setAttribute('y1', 0);
                vLine.setAttribute('x2', i * CELL_SIZE);
                vLine.setAttribute('y2', SVG_SIZE);
                svg.appendChild(vLine);
                
                // Horizontal lines
                const hLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                hLine.setAttribute('class', 'grid-line');
                hLine.setAttribute('x1', 0);
                hLine.setAttribute('y1', i * CELL_SIZE);
                hLine.setAttribute('x2', SVG_SIZE);
                hLine.setAttribute('y2', i * CELL_SIZE);
                svg.appendChild(hLine);
            }
        }

        // Create rectangle element
        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('class', 'rectangle');
        svg.appendChild(rect);

        // Create dimension text elements
        const widthText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        widthText.setAttribute('class', 'dimension-text');
        svg.appendChild(widthText);

        const heightText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        heightText.setAttribute('class', 'dimension-text');
        svg.appendChild(heightText);

        const areaText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        areaText.setAttribute('class', 'area-text');
        svg.appendChild(areaText);

        // Create corner circles
        const corners = {
            topLeft: createCorner('topLeft'),
            topRight: createCorner('topRight'),
            bottomLeft: createCorner('bottomLeft'),
            bottomRight: createCorner('bottomRight')
        };

        function createCorner(id) {
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('class', 'corner');
            circle.setAttribute('r', '8');
            circle.setAttribute('data-corner', id);
            svg.appendChild(circle);
            return circle;
        }

        // Convert SVG coordinates to grid coordinates
        function svgToGrid(svgX, svgY) {
            let gridX = Math.round(svgX / CELL_SIZE);
            let gridY = Math.round(svgY / CELL_SIZE);
            
            // Clamp to grid boundaries
            gridX = Math.max(0, Math.min(GRID_SIZE, gridX));
            gridY = Math.max(0, Math.min(GRID_SIZE, gridY));
            
            return { x: gridX, y: gridY };
        }

        // Get SVG coordinates from event (works for both mouse and touch)
        function getEventCoords(event) {
            const svgRect = svg.getBoundingClientRect();
            let clientX, clientY;
            
            if (event.touches && event.touches.length > 0) {
                clientX = event.touches[0].clientX;
                clientY = event.touches[0].clientY;
            } else {
                clientX = event.clientX;
                clientY = event.clientY;
            }
            
            return {
                x: clientX - svgRect.left,
                y: clientY - svgRect.top
            };
        }

        // Update rectangle and UI
        function updateRectangle() {
            const x = Math.min(rectangle.x1, rectangle.x2) * CELL_SIZE;
            const y = Math.min(rectangle.y1, rectangle.y2) * CELL_SIZE;
            const width = Math.abs(rectangle.x2 - rectangle.x1) * CELL_SIZE;
            const height = Math.abs(rectangle.y2 - rectangle.y1) * CELL_SIZE;
            
            rect.setAttribute('x', x);
            rect.setAttribute('y', y);
            rect.setAttribute('width', width);
            rect.setAttribute('height', height);
            
            // Update corners
            corners.topLeft.setAttribute('cx', rectangle.x1 * CELL_SIZE);
            corners.topLeft.setAttribute('cy', rectangle.y1 * CELL_SIZE);
            
            corners.topRight.setAttribute('cx', rectangle.x2 * CELL_SIZE);
            corners.topRight.setAttribute('cy', rectangle.y1 * CELL_SIZE);
            
            corners.bottomLeft.setAttribute('cx', rectangle.x1 * CELL_SIZE);
            corners.bottomLeft.setAttribute('cy', rectangle.y2 * CELL_SIZE);
            
            corners.bottomRight.setAttribute('cx', rectangle.x2 * CELL_SIZE);
            corners.bottomRight.setAttribute('cy', rectangle.y2 * CELL_SIZE);
            
            // Calculate dimensions
            const w = Math.abs(rectangle.x2 - rectangle.x1);
            const h = Math.abs(rectangle.y2 - rectangle.y1);
            
            // Update width text (bottom)
            widthText.setAttribute('x', x + width / 2);
            widthText.setAttribute('y', y + height + 25);
            widthText.textContent = w;
            
            // Update height text (right side)
            heightText.setAttribute('x', x + width + 25);
            heightText.setAttribute('y', y + height / 2 + 5);
            heightText.textContent = h;
            
            // Update area text (center)
            areaText.setAttribute('x', x + width / 2);
            areaText.setAttribute('y', y + height / 2 + 7);
            areaText.textContent = `${w} × ${h} = ${w * h}`;
        }

        // Handle drag start
        function startDrag(event) {
            const target = event.target;
            if (!target.classList.contains('corner')) return;
            
            event.preventDefault();
            
            const corner = target.getAttribute('data-corner');
            const coords = getEventCoords(event);
            
            dragState = {
                isDragging: true,
                corner: corner,
                startX: coords.x,
                startY: coords.y
            };
            
            target.classList.add('dragging');
        }

        // Handle drag move
        function drag(event) {
            if (!dragState.isDragging) return;
            
            event.preventDefault();
            
            const coords = getEventCoords(event);
            const gridPos = svgToGrid(coords.x, coords.y);
            
            const corner = dragState.corner;
            
            // Update rectangle coordinates based on which corner is being dragged
            switch(corner) {
                case 'topLeft':
                    // Ensure it doesn't flip over
                    if (gridPos.x < rectangle.x2 && gridPos.y < rectangle.y2) {
                        rectangle.x1 = gridPos.x;
                        rectangle.y1 = gridPos.y;
                    }
                    break;
                case 'topRight':
                    if (gridPos.x > rectangle.x1 && gridPos.y < rectangle.y2) {
                        rectangle.x2 = gridPos.x;
                        rectangle.y1 = gridPos.y;
                    }
                    break;
                case 'bottomLeft':
                    if (gridPos.x < rectangle.x2 && gridPos.y > rectangle.y1) {
                        rectangle.x1 = gridPos.x;
                        rectangle.y2 = gridPos.y;
                    }
                    break;
                case 'bottomRight':
                    if (gridPos.x > rectangle.x1 && gridPos.y > rectangle.y1) {
                        rectangle.x2 = gridPos.x;
                        rectangle.y2 = gridPos.y;
                    }
                    break;
            }
            
            updateRectangle();
        }

        // Handle drag end
        function endDrag(event) {
            if (!dragState.isDragging) return;
            
            event.preventDefault();
            
            // Remove dragging class from all corners
            Object.values(corners).forEach(corner => {
                corner.classList.remove('dragging');
            });
            
            dragState = {
                isDragging: false,
                corner: null,
                startX: 0,
                startY: 0
            };
        }

        // Event listeners for mouse
        svg.addEventListener('mousedown', startDrag);
        svg.addEventListener('mousemove', drag);
        svg.addEventListener('mouseup', endDrag);
        svg.addEventListener('mouseleave', endDrag);

        // Event listeners for touch
        svg.addEventListener('touchstart', startDrag, { passive: false });
        svg.addEventListener('touchmove', drag, { passive: false });
        svg.addEventListener('touchend', endDrag, { passive: false });
        svg.addEventListener('touchcancel', endDrag, { passive: false });

        // Initialize
        drawGrid();
        updateRectangle();
    </script>
</body>
</html>
"""

# Vis komponenten
components.html(html_code, height=700, scrolling=False)

st.markdown("---")
st.markdown("""
### Funktioner:
✅ **10×10 fast gitter** - Ternene ændrer aldrig størrelse  
✅ **Kun heltal** - Punkterne kan kun placeres i gitterkryds  
✅ **Kun rektangler** - Ingen diagonale eller skæve former  
✅ **Automatisk begrænsning** - Kan ikke trække uden for 10×10 området  
✅ **Touch-venlig** - Fungerer perfekt på tablets og smartphones  
✅ **Live opdatering** - Sidelængder og areal opdateres øjeblikkeligt  
""")
