// // For image zoom and pan in modal
// var scale = 1;
// var translateX = 0;
// var translateY = 0;
// var zoomableDiv = document.getElementById('zoomableDiv');
// var container = document.querySelector('.interactive-image-container');
//
// // Mouse/touch state
// var isDragging = false;
// var lastX = 0;
// var lastY = 0;
//
// // Apply transform with both scale and translate
// function applyTransform() {
//     zoomableDiv.style.transform = `scale(${scale}) translate(${translateX}px, ${translateY}px)`;
// }
//
// // Mouse wheel and trackpad zoom
// var lastWheelTime = 0;
// var wheelAccumulator = 0;
//
// container.addEventListener('wheel', (e) => {
//     e.preventDefault();
//
//     const currentTime = Date.now();
//     const timeDelta = currentTime - lastWheelTime;
//
//     // Detect if this is likely a Mac trackpad (rapid events with ctrlKey)
//     const isMacTrackpad = e.ctrlKey || (timeDelta < 50 && Math.abs(e.deltaY) > 10);
//
//     let zoomFactor;
//     if (isMacTrackpad) {
//         // For Mac trackpad: use smaller, more gradual changes
//         // Accumulate small changes for smoother zooming
//         wheelAccumulator += e.deltaY;
//
//         // Only apply zoom when accumulator reaches threshold
//         if (Math.abs(wheelAccumulator) > 20) {
//             zoomFactor = wheelAccumulator > 0 ? 0.95 : 1.05;
//             wheelAccumulator *= 0.7; // Reduce accumulator but don't reset completely
//         } else {
//             lastWheelTime = currentTime;
//             return; // Skip this event
//         }
//     } else {
//         // For regular mouse wheel: use normal zoom steps
//         zoomFactor = e.deltaY > 0 ? 0.9 : 1.1;
//         wheelAccumulator = 0; // Reset accumulator for mouse wheel
//     }
//
//     const newScale = Math.max(0.5, Math.min(3, scale * zoomFactor));
//
//     // Get cursor position relative to container
//     const rect = container.getBoundingClientRect();
//     const mouseX = e.clientX - rect.left - rect.width / 2;
//     const mouseY = e.clientY - rect.top - rect.height / 2;
//
//     // Adjust translation to zoom towards cursor position
//     const scaleRatio = newScale / scale;
//     translateX = mouseX * (1 - scaleRatio) + translateX * scaleRatio;
//     translateY = mouseY * (1 - scaleRatio) + translateY * scaleRatio;
//
//     scale = newScale;
//     lastWheelTime = currentTime;
//     applyTransform();
// });
//
// // Mouse drag for panning
// container.addEventListener('mousedown', (e) => {
//     if (scale > 1) { // Only allow panning when zoomed
//         isDragging = true;
//         lastX = e.clientX;
//         lastY = e.clientY;
//         container.style.cursor = 'grabbing';
//         e.preventDefault();
//     }
// });
//
// document.addEventListener('mousemove', (e) => {
//     if (isDragging) {
//         const deltaX = e.clientX - lastX;
//         const deltaY = e.clientY - lastY;
//
//         translateX += deltaX / scale; // Adjust for current scale
//         translateY += deltaY / scale;
//
//         lastX = e.clientX;
//         lastY = e.clientY;
//
//         applyTransform();
//         e.preventDefault();
//     }
// });
//
// document.addEventListener('mouseup', () => {
//     if (isDragging) {
//         isDragging = false;
//         container.style.cursor = scale > 1 ? 'grab' : 'default';
//     }
// });
//
// // Touch zoom (pinch)
// var initialDistance = 0;
// var initialScale = 1;
// var touchStartX = 0;
// var touchStartY = 0;
// var initialTranslateX = 0;
// var initialTranslateY = 0;
//
// container.addEventListener('touchstart', (e) => {
//     if (e.touches.length === 2) {
//         // Two finger pinch zoom
//         initialDistance = getDistance(e.touches[0], e.touches[1]);
//         initialScale = scale;
//         e.preventDefault();
//     } else if (e.touches.length === 1 && scale > 1) {
//         // Single finger pan when zoomed
//         isDragging = true;
//         touchStartX = e.touches[0].clientX;
//         touchStartY = e.touches[0].clientY;
//         initialTranslateX = translateX;
//         initialTranslateY = translateY;
//         e.preventDefault();
//     }
// });
//
// container.addEventListener('touchmove', (e) => {
//     if (e.touches.length === 2) {
//         // Handle pinch zoom
//         const currentDistance = getDistance(e.touches[0], e.touches[1]);
//         const ratio = currentDistance / initialDistance;
//         const dampedRatio = 1 + (ratio - 1) * 0.5; // 50% sensitivity
//         scale = Math.max(0.5, Math.min(3, initialScale * dampedRatio));
//         applyTransform();
//         e.preventDefault();
//     } else if (e.touches.length === 1 && isDragging) {
//         // Handle single finger pan
//         const deltaX = e.touches[0].clientX - touchStartX;
//         const deltaY = e.touches[0].clientY - touchStartY;
//
//         translateX = initialTranslateX + deltaX / scale;
//         translateY = initialTranslateY + deltaY / scale;
//
//         applyTransform();
//         e.preventDefault();
//     }
// });
//
// container.addEventListener('touchend', (e) => {
//     if (e.touches.length === 0) {
//         isDragging = false;
//     }
// });
//
// // Reset on double click/tap
// container.addEventListener('dblclick', () => {
//     scale = 1;
//     translateX = 0;
//     translateY = 0;
//     applyTransform();
//     container.style.cursor = 'default';
// });
//
// // Update cursor based on zoom level
// container.addEventListener('mouseenter', () => {
//     container.style.cursor = scale > 1 ? 'grab' : 'default';
// });
//
// function getDistance(touch1, touch2) {
//     const dx = touch1.clientX - touch2.clientX;
//     const dy = touch1.clientY - touch2.clientY;
//     return Math.sqrt(dx * dx + dy * dy);
// }
//
// // Prevent context menu on long press for mobile
// container.addEventListener('contextmenu', (e) => {
//     e.preventDefault();
// });