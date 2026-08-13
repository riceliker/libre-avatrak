<template>
  
  <div class="camera-control-container">
    <div class="camera-control-title-container">
      <h2 :style="{fontSize: '32px'}">Camera Control</h2>
      <div class="camera-control-status-container" :style="{ backgroundColor: status ? '#5af867': '#f85a5a' }">
        <p>{{ status ? 'Open' : 'Closed' }}</p>
      </div>
    </div>
    <div class="camera-control-buttons-container">
      <button class="camera-control-button" @click="open_camera">OpenCamera</button>
      <button class="camera-control-button" @click="close_camera">CloseCamera</button>
    </div>
    <div>
      <h2>Catch Data</h2>
      <div class="camera-control-data-container">
        <div class="camera-control-data-obj-container">
          <p>Eye-L: {{ face_data[0] }}</p>
          <p>Eye-R: {{ face_data[1] }}</p>
          <p>Mouse: {{ face_data[2] }}</p>
        </div>
        <div class="camera-control-data-obj-container">
          <p>Pitch: {{ face_data[3] }}</p>
          <p>Yaw: {{ face_data[4] }}</p>
          <p>Roll: {{ face_data[5] }}</p>
        </div>
      </div>
    </div>
  </div>  
</template>

<style>
.camera-control-container {
  display: flex;
  flex-direction: column;
  width: 420px;
  height: auto;
  background-color: #ecd3ec;
  border-radius: 10px;
  border: 2px solid #3b187d;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
}
.camera-control-title-container {
  flex-direction: row;
  display: flex;
  justify-content: space-between;
}
.camera-control-button {
  border: 2px solid #000000;
  border-radius: 10px;
  width: 150px;
  height: 50px;
  font-size: 16px;
}
.camera-control-buttons-container {
  width: auto;
  height: auto;
  display: flex;
  margin-top: 10px;
  flex-direction: row;
  justify-content: space-around;
}
.camera-control-status-container {
  display: flex;
  flex-direction: row;
  width: 120px;
  height: 30px;
  border-radius: 5px;
  border: #000000 2px solid;
  justify-content: center;
  font-size: 24px;
}
.camera-control-data-container {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}
.camera-control-data-obj-container {
  width: 100%;
  height: auto;
  display: flex;
  margin-left: 10px;
  margin-right: 10px;
  flex-direction: column;
  background-color: #ffffff;
  border: #3b187d 2px solid ;
  border-radius: 5px;
}
</style>

<script setup lang="ts">
import { ref } from 'vue';
import axios from 'axios';

const status = ref(false);
const face_data = ref<number[]>([0, 0, 0, 0, 0, 0]);
const face_data_stream = new EventSource(`${getServerBaseUrl()}/camera/query`);

function getServerBaseUrl() {
  const { protocol, host } = window.location;
  return `${protocol}//${host}`;
}

async function open_camera() {
  const response = await axios.get(`${getServerBaseUrl()}/camera/open`);
  const data = response.data;
  console.log('Camera opened:', data);
  if (data.code === 200) {
    status.value = true;
  } else {
    alert('Failed to open camera. Please check the console for details.');
  }
}

async function close_camera() {
  try {
    const response = await axios.get(`${getServerBaseUrl()}/camera/close`);
    const data = response.data;
    console.log('Camera closed:', data);
    if (data.code === 200) {
      status.value = false;
    } else {
      alert('Failed to close camera. Please check the console for details.');
    }
    status.value = false;
  } catch (error) {
    console.error('Error closing camera:', error);
  }
}

interface SSEPayload {
  face_data: number[];
}

face_data_stream.onmessage = function (e) {
  try{
  const data = JSON.parse(e.data) as SSEPayload;
  face_data.value = data.face_data;
  } catch {

  }
}
</script>