// visualizer.js

let scene, camera, renderer, controls, points, slider;
let minTime, maxTime, pointData = [];
let raycaster, mouse;
let ws;
const scalingFactor = 20;

// Create a debug overlay
const overlay = document.createElement('div');
overlay.style.position = 'absolute';
overlay.style.bottom = '10px';
overlay.style.left = '10px';
overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
overlay.style.color = 'white';
overlay.style.padding = '10px';
overlay.style.fontFamily = 'Arial, sans-serif';
overlay.style.zIndex = '100'; // Ensure overlay is on top
document.body.appendChild(overlay);

function init() {
    // Set up the scene, camera, and renderer
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 10000);
    camera.updateMatrix();
    renderer = new THREE.WebGLRenderer();
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.getElementById('visualizer').appendChild(renderer.domElement);

    // Add controls
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.25;
    controls.enableZoom = true;

    // Set up the slider
    slider = document.getElementById('slider');
    slider.addEventListener('input', updateTimeSlice);

    // Initialize raycaster and mouse vector
    initRaycaster();

    // Initialize WebSocket connection
    const params = new URLSearchParams(window.location.search);
    const datasetName = params.get('dataset_name');
    if (!datasetName) {
        console.error('No dataset_name query parameter provided');
        return;
    }
    initWebSocket(datasetName);

    // Resize listener
    window.addEventListener('resize', onWindowResize, true);
    window.addEventListener('mouseup', onPointerClick, true);

    // Initialize camera position
    camera.position.z = 200; // Adjusted for better visibility
}

function initRaycaster() {
    raycaster = new THREE.Raycaster(camera.position, camera.direction, 0, 100000);
    mouse = new THREE.Vector2();
    window.addEventListener('pointermove', onPointerMove);
    raycaster.params.Points.threshold = 0.5;
}

function onPointerMove(event) {
    // Convert mouse position to normalized device coordinates (-1 to +1)
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
}

function onPointerClick(){
    console.log('click!');
    raycaster.setFromCamera(mouse, camera);
    // Check intersections with the points
    const intersects = raycaster.intersectObject(points, false);

    if (intersects.length > 0) {
        const intersect = intersects[0];
        const index = intersect.index;
        if (index >= 0 && index < pointData.length) {
            const dataPoint = pointData[index];
            console.log(JSON.parse(dataPoint.additional_info));
            window.open(`https://huggingface.co/datasets/${JSON.parse(dataPoint.additional_info)['id']}`);
            overlay.textContent = `Additional Information: ${dataPoint.additional_info}`;
        }
    }
}

function initPoints() {
    if (pointData.length === 0) return;

    const numPoints = pointData.length;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(numPoints * 3);
    const colors = new Float32Array(numPoints * 3);

    pointData.forEach((point, index) => {
        const i = index * 3;
        positions[i] = point.x * scalingFactor; // Scaling factor
        positions[i + 1] = point.y * scalingFactor; // Scaling factor
        positions[i + 2] = point.z * scalingFactor; // Scaling factor

        // Default color (blue)
        colors[i] = 0;
        colors[i + 1] = 0;
        colors[i + 2] = 1;
    });

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const material = new THREE.PointsMaterial({ size: 0.1, vertexColors: true });
    points = new THREE.Points(geometry, material);
    scene.add(points);

    // Initial time slice update
    updateTimeSlice();
}

function updatePoints() {
    if (!points) return;

    const geometry = points.geometry;
    const numPoints = pointData.length;
    const positions = new Float32Array(numPoints * 3);
    const colors = new Float32Array(numPoints * 3);

    pointData.forEach((point, index) => {
        const i = index * 3;
        positions[i] = point.x * scalingFactor; // Scaling factor
        positions[i + 1] = point.y * scalingFactor; // Scaling factor
        positions[i + 2] = point.z * scalingFactor; // Scaling factor

        // Interpolate color from blue to white based on slider value
        const distance = Math.abs(point.w - parseFloat(slider.value));
        const maxDistance = maxTime - minTime;
        const t = 1 - Math.min(distance / maxDistance, 1);
        const color = new THREE.Color().lerpColors(new THREE.Color(0x0000ff), new THREE.Color(0xffffff), t);

        colors[i] = color.r;
        colors[i + 1] = color.g;
        colors[i + 2] = color.b;
    });

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    geometry.attributes.position.needsUpdate = true;
    geometry.attributes.color.needsUpdate = true;
    geometry.computeBoundingSphere();
}

function adjustCameraToDataset() {
    if (!pointData.length) return;

    const boundingBox = new THREE.Box3();
    pointData.forEach((point) => {
        const vector = new THREE.Vector3(point.x * 2, point.y * 2, point.z * 2);
        boundingBox.expandByPoint(vector);
    });

    const center = boundingBox.getCenter(new THREE.Vector3());
    const size = boundingBox.getSize(new THREE.Vector3());

    camera.position.set(center.x, center.y, size.length() * 1.5);
    camera.lookAt(center);
}

function initWebSocket(datasetName) {
    ws = new WebSocket('ws://localhost:8080/ws');

    ws.binaryType = 'arraybuffer'; // Set to handle binary data

    ws.onopen = () => {
        console.log('WebSocket connection established');
        ws.send(JSON.stringify({ type: 'start_stream', dataset_name: datasetName, batch_size: 1000 }));
    };

    ws.onmessage = (event) => {
        //const data = JSON.parse(event.data);
        //console.log(event);

        try {
            const closed = JSON.parse(event.data);
            if (closed.type === 'end_of_stream') {
                console.log('End of data stream');
                //adjustCameraToDataset();
                return;
            }
            console.log(closed);
            return;
        } catch (parseError) {
            console.log('continue');
        }



        if (event.error) {
            console.error(`Error: ${event.error}`);
            return;
        }

        // Decode base64 string
        const base64Data = event.data;
        const binaryString = atob(base64Data); // Base64 to binary string
        const uint8Array = new Uint8Array(binaryString.length);

        for (let i = 0; i < binaryString.length; i++) {
            uint8Array[i] = binaryString.charCodeAt(i);
        }

        // Decompress data
        try {
            const decompressedData = pako.ungzip(uint8Array, { to: 'string' });
            console.log('Decompressed data:', decompressedData);

            try {
                const parsedData = JSON.parse(decompressedData);
                console.log('Parsed data:', parsedData);

                pointData.push(...parsedData.data);


                if (!points) {
                    initPoints();
                } else {
                    updatePoints();
                }
            } catch (parseError) {
                console.error('Failed to parse JSON:', parseError);
            }
        } catch (decompressionError) {
            console.error('Failed to decompress data:', decompressionError);
        }
    };



    ws.onclose = () => {
        console.log('WebSocket connection closed');
        //adjustCameraToDataset();
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
}

function updateTimeSlice() {
    updatePoints();
}

function checkHover() {
    if (!points) return;

    // Update raycaster with the camera and mouse coordinates
    camera.updateMatrixWorld(); // Ensure the raycaster has the latest world matrix

    raycaster.setFromCamera(mouse, camera);
    // Check intersections with the points
    const intersects = raycaster.intersectObject(points, false);

    if (intersects.length > 0) {
        const intersect = intersects[0];
        const index = intersect.index;
        if (index >= 0 && index < pointData.length) {
            const dataPoint = pointData[index];
            overlay.textContent = `Additional Information: ${dataPoint.additional_info}`;
        }
    } else {
        overlay.textContent = `Camera Position: (${camera.position.x.toFixed(2)}, 
            ${camera.position.y.toFixed(2)}, 
            ${camera.position.z.toFixed(2)})\n
            Slider Value: ${slider.value},
            n points: ${pointData.length}`;
    }
}

function animate() {
    requestAnimationFrame(animate);
    controls.update();
    checkHover();
    renderer.render(scene, camera);
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

// Initialize
init();
animate();
