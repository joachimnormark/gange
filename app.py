import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Gangemaskine", layout="wide")

st.title("✖️ Gangemaskine")

# Vælger for grid-størrelse
grid_size = st.selectbox(
    "Vælg antal tern:",
    options=[10, 20, 30],
    index=0,
    format_func=lambda x: f"{x}×{x} tern"
)

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
            fill: rgba(250, 245, 192, 0.5);
            stroke: #4285f4;
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
        }
        .dimension-text {
            font-weight: bold;
            fill: #333;
            text-anchor: middle;
            pointer-events: none;
            user-select: none;
        }
        .text-background {
            fill: white;
            stroke: white;
            stroke-width: 2;
            pointer-events: none;
        }
        .area-text {
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
        const GRID_SIZE = """ + str(grid_size) + """;
        const CELL_SIZE = SVG_SIZE / GRID_SIZE;
        
        // Scale text sizes based on grid size
        const BASE_FONT_SIZE = GRID_SIZE === 10 ? 16 : (GRID_SIZE === 20 ? 12 : 10);
        const AREA_FONT_SIZE = GRID_SIZE === 10 ? 20 : (GRID_SIZE === 20 ? 14 : 11);
        const CORNER_RADIUS = GRID_SIZE === 10 ? 8 : (GRID_SIZE === 20 ? 6 : 5);
        
        // State - start med 5×5 rektangel centreret
        const startOffset = Math.floor((GRID_SIZE - 5) / 2);
        let rectangle = {
            x1: startOffset, y1: startOffset,
            x2: startOffset + 5, y2: startOffset + 5
        };
        
        let dragState = {
            isDragging: false,
            corner: null,
            startX: 0,
            startY: 0
        };

        // Initialize SVG
        const svg = document.getElementById('canvas');
        
        // Draw grid first (so it's behind everything)
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

        // Draw grid first
        drawGrid();

        // Create rectangle element (after grid)
        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('class', 'rectangle');
        svg.appendChild(rect);

        // Create text backgrounds (before text, so they're behind)
        const widthTextBg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        widthTextBg.setAttribute('class', 'text-background');
        svg.appendChild(widthTextBg);

        const heightTextBg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        heightTextBg.setAttribute('class', 'text-background');
        svg.appendChild(heightTextBg);

        // Create dimension text elements (after grid)
        const widthText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        widthText.setAttribute('class', 'dimension-text');
        widthText.setAttribute('font-size', BASE_FONT_SIZE);
        svg.appendChild(widthText);

        const heightText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        heightText.setAttribute('class', 'dimension-text');
        heightText.setAttribute('font-size', BASE_FONT_SIZE);
        svg.appendChild(heightText);

        const areaText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        areaText.setAttribute('class', 'area-text');
        areaText.setAttribute('font-size', AREA_FONT_SIZE);
        svg.appendChild(areaText);

        // Create corner circles (after grid)
        const corners = {
            topLeft: createCorner('topLeft'),
            topRight: createCorner('topRight'),
            bottomLeft: createCorner('bottomLeft'),
            bottomRight: createCorner('bottomRight')
        };

        function createCorner(id) {
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('class', 'corner');
            circle.setAttribute('r', CORNER_RADIUS);
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
            
            // Update width text and background (bottom or top depending on position)
            const widthTextX = x + width / 2;
            let widthTextY;
            if (rectangle.y2 === GRID_SIZE) {
                // If at bottom edge, show above rectangle
                widthTextY = y - 10;
            } else {
                // Normal position below rectangle
                widthTextY = y + height + 25;
            }
            widthText.setAttribute('x', widthTextX);
            widthText.setAttribute('y', widthTextY);
            widthText.textContent = w;
            
            // Calculate background sizes based on font size and number of digits
            const bgPadding = GRID_SIZE === 10 ? 15 : (GRID_SIZE === 20 ? 13 : 11);
            const bgWidth = GRID_SIZE === 10 ? 30 : (GRID_SIZE === 20 ? 28 : 26);
            const bgHeight = GRID_SIZE === 10 ? 22 : (GRID_SIZE === 20 ? 18 : 16);
            
            // Position width text background
            widthTextBg.setAttribute('x', widthTextX - bgPadding);
            widthTextBg.setAttribute('y', widthTextY - bgHeight + 6);
            widthTextBg.setAttribute('width', bgWidth);
            widthTextBg.setAttribute('height', bgHeight);
            widthTextBg.setAttribute('rx', 3);
            
            // Update height text and background (right or left side depending on position)
            const heightTextY = y + height / 2 + 5;
            let heightTextX;
            if (rectangle.x2 === GRID_SIZE) {
                // If at right edge, show to the left of rectangle
                heightTextX = x - 15;
            } else {
                // Normal position to the right of rectangle
                heightTextX = x + width + 25;
            }
            heightText.setAttribute('x', heightTextX);
            heightText.setAttribute('y', heightTextY);
            heightText.textContent = h;
            
            // Position height text background
            heightTextBg.setAttribute('x', heightTextX - bgPadding);
            heightTextBg.setAttribute('y', heightTextY - bgHeight + 6);
            heightTextBg.setAttribute('width', bgWidth);
            heightTextBg.setAttribute('height', bgHeight);
            heightTextBg.setAttribute('rx', 3);
            
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
        updateRectangle();
    </script>
</body>
</html>
"""

# Vis komponenten
components.html(html_code, height=700, scrolling=False, key=f"grid_{grid_size}")
